import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

try:
    import timm
except ImportError as exc:
    raise ImportError("timm is required for convnext_tiny. Please install timm in the rsna env.") from exc

try:
    from sklearn.metrics import roc_auc_score
except ImportError as exc:
    raise ImportError("scikit-learn is required for AUC computation.") from exc


LABELS: List[str] = [
    "ACL",
    "MCL",
    "Medial Meniscus",
    "Lateral Meniscus",
    "Medial OA",
    "Lateral OA",
    "PF OA",
    "Effusion",
    "Synovitis",
    "Baker's",
    "Contusion",
    "Fracture",
]

LABELER_RECALL_WEIGHTS: Dict[str, float] = {
    "ACL": 0.67,
    "MCL": 0.78,
    "Medial Meniscus": 0.85,
    "Lateral Meniscus": 0.70,
    "Medial OA": 0.60,
    "Lateral OA": 0.64,
    "PF OA": 0.48,
    "Effusion": 0.83,
    "Synovitis": 0.44,
    "Baker's": 0.75,
    "Contusion": 0.79,
    "Fracture": 0.56,
}


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def normalize_name(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum())


def infer_study_id_column(df: pd.DataFrame) -> str:
    candidates = [
        "study_id",
        "StudyInstanceUID",
        "study_uid",
        "study",
        "id",
        "ID",
    ]
    for c in candidates:
        if c in df.columns:
            return c

    normalized = {normalize_name(c): c for c in df.columns}
    for key in ["studyid", "studyinstanceuid", "studyuid", "id"]:
        if key in normalized:
            return normalized[key]

    raise ValueError(f"Could not infer study id column from columns: {list(df.columns)}")


def infer_label_column(df: pd.DataFrame, label: str, explicit_map: Optional[Dict[str, str]] = None) -> str:
    if explicit_map and label in explicit_map:
        col = explicit_map[label]
        if col not in df.columns:
            raise ValueError(f"Mapped column '{col}' for label '{label}' not found in train.csv")
        return col

    direct = [label, f"{label}_label", f"{label}_gt"]
    for c in direct:
        if c in df.columns:
            return c

    target_key = normalize_name(label)
    norm_map = {normalize_name(c): c for c in df.columns}
    for suffix in ["", "label", "gt", "target", "positive"]:
        k = f"{target_key}{suffix}"
        if k in norm_map:
            return norm_map[k]

    raise ValueError(
        f"Could not infer train.csv column for label '{label}'. "
        f"Pass --gold-column-map-json to define an explicit mapping."
    )


def load_gold_labels(train_csv_path: str, labels: List[str], gold_column_map: Optional[Dict[str, str]]) -> pd.DataFrame:
    df = pd.read_csv(train_csv_path)
    sid_col = infer_study_id_column(df)

    out = pd.DataFrame()
    out["study_id"] = df[sid_col].astype(str)

    for label in labels:
        col = infer_label_column(df, label, gold_column_map)
        out[label] = pd.to_numeric(df[col], errors="coerce")

    out["is_gold_study"] = 1
    return out


def load_pseudo_labels(labeler_parquet_path: str, labels: List[str]) -> pd.DataFrame:
    df = pd.read_parquet(labeler_parquet_path)
    sid_col = infer_study_id_column(df)

    out = pd.DataFrame()
    out["study_id"] = df[sid_col].astype(str)

    for label in labels:
        pred_col = f"{label}_pred"
        if pred_col not in df.columns:
            raise ValueError(f"Missing pseudo-label column: {pred_col}")
        out[label] = pd.to_numeric(df[pred_col], errors="coerce")

    return out


def merge_gold_and_pseudo_labels(gold_df: pd.DataFrame, pseudo_df: pd.DataFrame, labels: List[str]) -> pd.DataFrame:
    merged = pseudo_df.copy()
    merged = merged.drop_duplicates(subset=["study_id"]).reset_index(drop=True)

    gold_indexed = gold_df.drop_duplicates(subset=["study_id"]).set_index("study_id")

    for label in labels:
        merged[f"{label}__source"] = 0  # 0 pseudo, 1 gold

    sid_to_idx = {sid: i for i, sid in enumerate(merged["study_id"].tolist())}

    for sid, row in gold_indexed.iterrows():
        if sid not in sid_to_idx:
            continue
        i = sid_to_idx[sid]
        for label in labels:
            v = row[label]
            if pd.notna(v):
                merged.at[i, label] = float(v)
                merged.at[i, f"{label}__source"] = 1

    merged["is_gold_study"] = merged[[f"{l}__source" for l in labels]].max(axis=1).astype(int)
    return merged


def infer_fold_column(df: pd.DataFrame) -> str:
    for c in ["fold", "Fold", "cv_fold"]:
        if c in df.columns:
            return c
    raise ValueError(f"Could not infer fold column from {list(df.columns)}")


def attach_folds(label_df: pd.DataFrame, folds_parquet_path: str) -> pd.DataFrame:
    fdf = pd.read_parquet(folds_parquet_path)
    sid_col = infer_study_id_column(fdf)
    fold_col = infer_fold_column(fdf)

    fdf2 = fdf[[sid_col, fold_col]].copy()
    fdf2.columns = ["study_id", "fold"]
    fdf2["study_id"] = fdf2["study_id"].astype(str)

    out = label_df.merge(fdf2, on="study_id", how="left")
    out = out[out["fold"].notna()].copy()
    out["fold"] = out["fold"].astype(int)
    out = out.reset_index(drop=True)
    return out


def decode_slot_mask(mask_obj: np.ndarray) -> np.ndarray:
    arr = np.asarray(mask_obj)
    if arr.ndim == 0:
        m = int(arr.item())
        bits = np.array([(m >> i) & 1 for i in range(6)], dtype=np.float32)
        return bits
    if arr.ndim == 1 and arr.shape[0] == 6:
        return arr.astype(np.float32)
    if arr.ndim > 1:
        flat = arr.reshape(-1)
        if flat.shape[0] == 6:
            return flat.astype(np.float32)
    raise ValueError(f"Unsupported slot mask shape: {arr.shape}")


def load_cached_study(npz_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    with np.load(npz_path, allow_pickle=True) as z:
        keys = list(z.keys())

        tensor = None
        for k in ["x", "tensor", "images", "arr_0"]:
            if k in z:
                cand = z[k]
                if cand.ndim == 4:
                    tensor = cand
                    break
        if tensor is None:
            for k in keys:
                cand = z[k]
                if isinstance(cand, np.ndarray) and cand.ndim == 4:
                    tensor = cand
                    break

        if tensor is None:
            raise ValueError(f"Could not find 4D tensor in {npz_path}; keys={keys}")

        slot_mask = None
        for k in ["slot_mask", "mask", "arr_1"]:
            if k in z:
                try:
                    slot_mask = decode_slot_mask(z[k])
                    break
                except Exception:
                    pass

        if slot_mask is None:
            for k in keys:
                cand = z[k]
                try:
                    sm = decode_slot_mask(cand)
                    slot_mask = sm
                    break
                except Exception:
                    continue

        if slot_mask is None:
            slot_mask = np.ones(6, dtype=np.float32)

    tensor = tensor.astype(np.float32)
    if tensor.shape != (6, 24, 128, 128):
        raise ValueError(f"Expected tensor shape (6,24,128,128) in {npz_path}, got {tensor.shape}")

    return tensor, slot_mask


class GoldKneeDataset(Dataset):
    """Full-dataset version: reads tensor cache and returns labels + masks + source flags."""

    def __init__(self, df: pd.DataFrame, tensors_dir: str, labels: List[str]) -> None:
        self.df = df.reset_index(drop=True)
        self.tensors_dir = Path(tensors_dir)
        self.labels = labels

    def __len__(self) -> int:
        return len(self.df)

    def _npz_path(self, study_id: str) -> Path:
        return self.tensors_dir / f"{study_id}.npz"

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]
        sid = str(row["study_id"])

        npz_path = self._npz_path(sid)
        if not npz_path.exists():
            raise FileNotFoundError(f"Tensor cache file not found: {npz_path}")

        x, slot_mask = load_cached_study(npz_path)

        y = np.array([row[label] for label in self.labels], dtype=np.float32)
        y_source = np.array([row[f"{label}__source"] for label in self.labels], dtype=np.float32)
        y_mask = (y != -1).astype(np.float32)

        # For BCEWithLogits we keep targets in {0,1}; masked entries can be any value.
        y = np.where(y == -1, 0.0, y)

        return {
            "x": torch.from_numpy(x),                # [6,24,128,128]
            "slot_mask": torch.from_numpy(slot_mask),
            "y": torch.from_numpy(y),                # [12]
            "y_mask": torch.from_numpy(y_mask),      # [12]
            "y_source": torch.from_numpy(y_source),  # [12]
            "study_id": sid,
            "is_gold_study": torch.tensor(float(row["is_gold_study"]), dtype=torch.float32),
        }


class SlotAttentionPool(nn.Module):
    """Attention pooling over 6 slots with explicit masking for missing slots."""

    def __init__(self, in_dim: int, attn_dim: int = 256, dropout: float = 0.0) -> None:
        super().__init__()
        self.score = nn.Sequential(
            nn.Linear(in_dim, attn_dim),
            nn.Tanh(),
            nn.Dropout(dropout),
            nn.Linear(attn_dim, 1),
        )

    def forward(self, h: torch.Tensor, slot_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # h: [B,S,D], slot_mask: [B,S] in {0,1}
        raw = self.score(h).squeeze(-1)  # [B,S]
        valid = slot_mask > 0
        raw = raw.masked_fill(~valid, -1e9)

        attn = torch.softmax(raw, dim=1)
        attn = attn * valid.float()
        denom = attn.sum(dim=1, keepdim=True).clamp_min(1e-6)
        attn = attn / denom

        pooled = torch.sum(attn.unsqueeze(-1) * h, dim=1)
        return pooled, attn


class GatedAttentionMIL(nn.Module):
    """
    Gated-attention MIL over the 24 slices inside each slot.

    For each slice feature h_k, we compute:
        a_k = w^T [ tanh(V h_k) * sigmoid(U h_k) ]
    then softmax-normalize a_k across slices and produce weighted sum of h_k.

    There is no independent per-slice validity mask in this dataset. We derive validity
    directly from slot_mask: if a slot is present, all 24 slices are considered valid;
    if absent, the slot is excluded from MIL attention and output is zeroed explicitly.
    """

    def __init__(self, in_dim: int, attn_dim: int = 256, dropout: float = 0.0) -> None:
        super().__init__()
        self.v = nn.Linear(in_dim, attn_dim)
        self.u = nn.Linear(in_dim, attn_dim)
        self.w = nn.Linear(attn_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, h: torch.Tensor, slot_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # h: [B,S,K,D], slot_mask: [B,S]
        gate = torch.tanh(self.v(h)) * torch.sigmoid(self.u(h))
        gate = self.dropout(gate)
        logits = self.w(gate).squeeze(-1)  # [B,S,K]

        slot_valid = (slot_mask > 0).unsqueeze(-1)  # [B,S,1]

        # Exclude missing slots from MIL attention (explicit, not relying on zeroed cache values).
        logits = logits.masked_fill(~slot_valid, -1e9)
        attn = torch.softmax(logits, dim=-1)

        # Keep attention strictly zero for invalid slots and re-normalize valid ones.
        attn = attn * slot_valid.float()
        denom = attn.sum(dim=-1, keepdim=True).clamp_min(1e-6)
        attn = attn / denom

        pooled = torch.sum(attn.unsqueeze(-1) * h, dim=-2)  # [B,S,D]
        pooled = pooled * slot_valid.float()

        return pooled, attn


class FullKneeModel(nn.Module):
    def __init__(
        self,
        num_labels: int = 12,
        backbone_name: str = "convnext_tiny",
        pretrained: bool = True,
        in_chans: int = 1,
        mil_attn_dim: int = 256,
        slot_attn_dim: int = 256,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            in_chans=in_chans,
            num_classes=0,
            global_pool="avg",
        )

        if hasattr(self.backbone, "num_features"):
            feat_dim = int(self.backbone.num_features)
        else:
            raise ValueError("Backbone missing num_features; unsupported timm model config.")

        self.slice_pool = GatedAttentionMIL(in_dim=feat_dim, attn_dim=mil_attn_dim, dropout=dropout)
        self.slot_pool = SlotAttentionPool(in_dim=feat_dim, attn_dim=slot_attn_dim, dropout=dropout)
        self.head = nn.Linear(feat_dim, num_labels)

    def forward(self, x: torch.Tensor, slot_mask: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x: [B,6,24,128,128]
        b, s, k, h, w = x.shape
        x = x.reshape(b * s * k, 1, h, w)

        f = self.backbone(x)  # [B*S*K,D]
        d = f.shape[-1]
        f = f.reshape(b, s, k, d)

        slot_features, slice_attn = self.slice_pool(f, slot_mask)
        study_features, slot_attn = self.slot_pool(slot_features, slot_mask)
        logits = self.head(study_features)

        return {
            "logits": logits,
            "slice_attn": slice_attn,
            "slot_attn": slot_attn,
        }


def build_label_confidence_tensor(labels: List[str], device: torch.device) -> torch.Tensor:
    vals = [float(LABELER_RECALL_WEIGHTS[label]) for label in labels]
    return torch.tensor(vals, dtype=torch.float32, device=device)


def masked_confidence_weighted_bce_with_logits(
    logits: torch.Tensor,
    targets: torch.Tensor,
    target_mask: torch.Tensor,
    source_flag: torch.Tensor,
    label_confidence: torch.Tensor,
    base_pseudo_weight: float,
) -> torch.Tensor:
    # target_mask: 1 for valid labels, 0 for abstained (-1) labels.
    valid = target_mask.float()

    pseudo_weight = base_pseudo_weight * label_confidence.unsqueeze(0)  # [B,12]
    sample_label_weight = torch.where(source_flag > 0.5, torch.ones_like(pseudo_weight), pseudo_weight)
    sample_label_weight = sample_label_weight * valid

    bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
    denom = sample_label_weight.sum().clamp_min(1e-6)
    return (bce * sample_label_weight).sum() / denom


def safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    valid = np.isfinite(y_true) & np.isfinite(y_score)
    y_true = y_true[valid]
    y_score = y_score[valid]

    if y_true.size < 2:
        return float("nan")
    uniq = np.unique(y_true)
    if uniq.size < 2:
        return float("nan")

    try:
        return float(roc_auc_score(y_true, y_score))
    except Exception:
        return float("nan")


def compute_auc_table(
    y_true: np.ndarray,
    y_score: np.ndarray,
    y_mask: np.ndarray,
    labels: List[str],
    subset: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    n = y_true.shape[0]
    if subset is None:
        subset = np.ones(n, dtype=bool)

    for j, label in enumerate(labels):
        m = (y_mask[:, j] > 0.5) & subset
        auc = safe_auc(y_true[m, j], y_score[m, j]) if np.any(m) else float("nan")
        out[label] = auc
    return out


def mean_valid_auc(auc_table: Dict[str, float]) -> float:
    vals = [v for v in auc_table.values() if np.isfinite(v)]
    if not vals:
        return float("nan")
    return float(np.mean(vals))


def format_auc(v: float) -> str:
    return "nan" if not np.isfinite(v) else f"{v:.3f}"


def run_epoch_train(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    device: torch.device,
    label_confidence: torch.Tensor,
    base_pseudo_weight: float,
    amp_enabled: bool,
) -> float:
    model.train()
    total_loss = 0.0
    total_count = 0

    for batch in loader:
        x = batch["x"].to(device, non_blocking=True)
        slot_mask = batch["slot_mask"].to(device, non_blocking=True)
        y = batch["y"].to(device, non_blocking=True)
        y_mask = batch["y_mask"].to(device, non_blocking=True)
        y_source = batch["y_source"].to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        with torch.cuda.amp.autocast(enabled=amp_enabled):
            out = model(x, slot_mask)
            loss = masked_confidence_weighted_bce_with_logits(
                logits=out["logits"],
                targets=y,
                target_mask=y_mask,
                source_flag=y_source,
                label_confidence=label_confidence,
                base_pseudo_weight=base_pseudo_weight,
            )

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        bs = x.shape[0]
        total_loss += loss.item() * bs
        total_count += bs

    return total_loss / max(1, total_count)


@torch.no_grad()
def run_epoch_valid(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    amp_enabled: bool,
) -> Dict[str, Any]:
    model.eval()

    logits_list = []
    y_list = []
    y_mask_list = []
    y_source_list = []
    sid_list = []
    gold_study_list = []

    for batch in loader:
        x = batch["x"].to(device, non_blocking=True)
        slot_mask = batch["slot_mask"].to(device, non_blocking=True)

        with torch.cuda.amp.autocast(enabled=amp_enabled):
            out = model(x, slot_mask)

        logits = out["logits"].detach().cpu().numpy()
        y = batch["y"].numpy()
        y_mask = batch["y_mask"].numpy()
        y_source = batch["y_source"].numpy()

        logits_list.append(logits)
        y_list.append(y)
        y_mask_list.append(y_mask)
        y_source_list.append(y_source)
        sid_list.extend(batch["study_id"])
        gold_study_list.extend(batch["is_gold_study"].numpy().tolist())

    return {
        "logits": np.concatenate(logits_list, axis=0),
        "y": np.concatenate(y_list, axis=0),
        "y_mask": np.concatenate(y_mask_list, axis=0),
        "y_source": np.concatenate(y_source_list, axis=0),
        "study_id": np.array(sid_list, dtype=object),
        "is_gold_study": np.array(gold_study_list, dtype=np.float32),
    }


def print_auc_table(title: str, auc_table: Dict[str, float]) -> None:
    print("\n" + title)
    print("-" * len(title))
    for label in LABELS:
        print(f"{label:18s}: {format_auc(auc_table[label])}")
    print(f"{'MEAN':18s}: {format_auc(mean_valid_auc(auc_table))}")


def train_one_fold(
    fold: int,
    full_df: pd.DataFrame,
    args: argparse.Namespace,
    device: torch.device,
    outdir: Path,
) -> Dict[str, Any]:
    trn_df = full_df[full_df["fold"] != fold].reset_index(drop=True)
    val_df = full_df[full_df["fold"] == fold].reset_index(drop=True)

    train_ds = GoldKneeDataset(trn_df, args.tensors_dir, LABELS)
    valid_ds = GoldKneeDataset(val_df, args.tensors_dir, LABELS)

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True,
        drop_last=False,
    )
    valid_loader = DataLoader(
        valid_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
        drop_last=False,
    )

    model = FullKneeModel(
        num_labels=len(LABELS),
        backbone_name=args.backbone,
        pretrained=not args.no_pretrained,
        in_chans=1,
        mil_attn_dim=args.mil_attn_dim,
        slot_attn_dim=args.slot_attn_dim,
        dropout=args.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda" and not args.no_amp))
    amp_enabled = device.type == "cuda" and not args.no_amp

    label_confidence = build_label_confidence_tensor(LABELS, device)

    best_auc = -math.inf
    best_epoch = -1
    best_payload: Optional[Dict[str, Any]] = None
    bad_epochs = 0

    ckpt_path = outdir / f"fold{fold}_best.pt"

    for epoch in range(1, args.epochs + 1):
        train_loss = run_epoch_train(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            scaler=scaler,
            device=device,
            label_confidence=label_confidence,
            base_pseudo_weight=args.base_pseudo_weight,
            amp_enabled=amp_enabled,
        )

        val_out = run_epoch_valid(model, valid_loader, device, amp_enabled)
        val_auc_table = compute_auc_table(
            y_true=val_out["y"],
            y_score=val_out["logits"],
            y_mask=val_out["y_mask"],
            labels=LABELS,
        )
        val_mean_auc = mean_valid_auc(val_auc_table)

        print(
            f"Fold {fold} | Epoch {epoch:03d} | "
            f"train_loss={train_loss:.5f} | val_mean_auc={format_auc(val_mean_auc)}"
        )

        improved = np.isfinite(val_mean_auc) and (val_mean_auc > best_auc + 1e-6)
        if improved:
            best_auc = val_mean_auc
            best_epoch = epoch
            best_payload = val_out
            bad_epochs = 0

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "epoch": epoch,
                    "val_mean_auc": val_mean_auc,
                    "args": vars(args),
                    "labels": LABELS,
                },
                ckpt_path,
            )
        else:
            bad_epochs += 1

        if bad_epochs >= args.patience:
            print(f"Fold {fold}: early stopping at epoch {epoch} (best epoch {best_epoch})")
            break

    if best_payload is None:
        raise RuntimeError(f"Fold {fold}: no valid checkpoint produced.")

    print(f"Fold {fold}: best_epoch={best_epoch}, best_val_mean_auc={format_auc(best_auc)}")
    return {
        "fold": fold,
        "best_epoch": best_epoch,
        "best_val_mean_auc": best_auc,
        "ckpt_path": str(ckpt_path),
        "val_payload": best_payload,
        "val_df": val_df,
    }


def save_oof_npz(
    out_path: Path,
    logits: np.ndarray,
    labels: np.ndarray,
    masks: np.ndarray,
    study_ids: np.ndarray,
    source_flags: np.ndarray,
    is_gold_study: np.ndarray,
) -> None:
    np.savez_compressed(
        out_path,
        logits=logits,
        labels=labels,
        masks=masks,
        study_ids=study_ids,
        source_flags=source_flags,
        is_gold_study=is_gold_study,
        label_names=np.array(LABELS, dtype=object),
    )


def parse_gold_column_map(json_str: Optional[str]) -> Optional[Dict[str, str]]:
    if not json_str:
        return None
    parsed = json.loads(json_str)
    if not isinstance(parsed, dict):
        raise ValueError("--gold-column-map-json must be a JSON object")
    return {str(k): str(v) for k, v in parsed.items()}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train full RSNA model on gold + pseudo labels")

    p.add_argument("--train-csv", type=str, default=r"data\train.csv")
    p.add_argument("--labeler-parquet", type=str, default=r"data\labeler_checkpoint_FULL.parquet")
    p.add_argument("--folds-parquet", type=str, default=r"data\folds.parquet")
    p.add_argument("--tensors-dir", type=str, default=r"data\tensors")
    p.add_argument("--outdir", type=str, default=r"outputs\06_train_full")

    p.add_argument("--gold-column-map-json", type=str, default=None)

    p.add_argument("--backbone", type=str, default="convnext_tiny")
    p.add_argument("--no-pretrained", action="store_true")
    p.add_argument("--mil-attn-dim", type=int, default=256)
    p.add_argument("--slot-attn-dim", type=int, default=256)
    p.add_argument("--dropout", type=float, default=0.1)

    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--patience", type=int, default=5)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--weight-decay", type=float, default=1e-4)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--base-pseudo-weight", type=float, default=0.3)
    p.add_argument("--no-amp", action="store_true")

    p.add_argument("--folds", type=str, default="0,1,2,3,4", help="Comma-separated folds to run")

    return p.parse_args()


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    gold_map = parse_gold_column_map(args.gold_column_map_json)
    gold_df = load_gold_labels(args.train_csv, LABELS, gold_map)
    pseudo_df = load_pseudo_labels(args.labeler_parquet, LABELS)
    full_df = merge_gold_and_pseudo_labels(gold_df, pseudo_df, LABELS)
    full_df = attach_folds(full_df, args.folds_parquet)

    fold_list = [int(x.strip()) for x in str(args.folds).split(",") if x.strip()]
    print(f"Running folds: {fold_list}")
    print(f"Total studies with folds: {len(full_df)}")
    print(f"Gold studies in merged set: {int(full_df['is_gold_study'].sum())}")

    n = len(full_df)
    num_labels = len(LABELS)

    oof_logits = np.full((n, num_labels), np.nan, dtype=np.float32)
    oof_labels = np.full((n, num_labels), np.nan, dtype=np.float32)
    oof_masks = np.zeros((n, num_labels), dtype=np.float32)
    oof_sources = np.zeros((n, num_labels), dtype=np.float32)
    oof_gold_study = full_df["is_gold_study"].to_numpy(dtype=np.float32)
    oof_study_ids = full_df["study_id"].astype(str).to_numpy(dtype=object)

    fold_summaries = []

    for fold in fold_list:
        result = train_one_fold(fold, full_df, args, device, outdir)
        val_df = result["val_df"]
        val_payload = result["val_payload"]

        # map validation rows back to full_df indices by study_id
        val_sid_to_payload_idx = {sid: i for i, sid in enumerate(val_payload["study_id"].tolist())}

        for global_idx, sid in enumerate(full_df["study_id"].astype(str).tolist()):
            if int(full_df.iloc[global_idx]["fold"]) != fold:
                continue
            i = val_sid_to_payload_idx[sid]
            oof_logits[global_idx] = val_payload["logits"][i]
            oof_labels[global_idx] = val_payload["y"][i]
            oof_masks[global_idx] = val_payload["y_mask"][i]
            oof_sources[global_idx] = val_payload["y_source"][i]

        fold_summaries.append(
            {
                "fold": fold,
                "best_epoch": result["best_epoch"],
                "best_val_mean_auc": result["best_val_mean_auc"],
                "ckpt_path": result["ckpt_path"],
            }
        )

    save_oof_npz(
        out_path=outdir / "oof_full_cv.npz",
        logits=oof_logits,
        labels=oof_labels,
        masks=oof_masks,
        study_ids=oof_study_ids,
        source_flags=oof_sources,
        is_gold_study=oof_gold_study,
    )

    all_auc = compute_auc_table(oof_labels, oof_logits, oof_masks, LABELS)
    gold_subset = oof_gold_study > 0.5
    gold_auc = compute_auc_table(oof_labels, oof_logits, oof_masks, LABELS, subset=gold_subset)

    print_auc_table("OOF AUC (All Samples)", all_auc)
    print_auc_table("OOF AUC (Gold-Only Samples)", gold_auc)

    print("\nFold summary")
    print("------------")
    for fs in fold_summaries:
        print(
            f"fold={fs['fold']} | best_epoch={fs['best_epoch']} | "
            f"best_val_mean_auc={format_auc(fs['best_val_mean_auc'])} | "
            f"ckpt={fs['ckpt_path']}"
        )

    print(f"\nSaved OOF bundle: {outdir / 'oof_full_cv.npz'}")


if __name__ == "__main__":
    main()
