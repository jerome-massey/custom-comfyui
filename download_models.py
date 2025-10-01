#!/usr/bin/env python3
"""
ComfyUI Model Downloader
Downloads models, LoRAs, and other files from one or more manifest files.
Supports duplicate detection and manifest combining.
"""

import os
import sys
import json
import requests
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
import argparse
from typing import List, Dict, Optional
from collections import defaultdict

COMFYUI_PATH = os.environ.get('COMFYUI_PATH', '/app/ComfyUI')

class ModelManifest:
    """Handles loading, combining, and deduplicating model manifests."""
    
    def __init__(self):
        self.models = []
        self.custom_nodes = []
        self.seen_models = {}  # Track by URL to detect duplicates
        self.seen_nodes = {}   # Track by repo URL to detect duplicates
    
    def load_manifest(self, source: str) -> Dict:
        """Load manifest from URL or local file."""
        try:
            if source.startswith('http://') or source.startswith('https://'):
                print(f"📥 Fetching manifest from: {source}")
                response = requests.get(source, timeout=30)
                response.raise_for_status()
                return response.json()
            else:
                print(f"📂 Loading manifest from: {source}")
                with open(source, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"✗ Error loading manifest from {source}: {str(e)}")
            return None
    
    def add_manifest(self, manifest: Dict, source: str) -> tuple:
        """Add a manifest, tracking duplicates."""
        if not manifest:
            return 0, 0, 0, 0
        
        models_added = 0
        models_skipped = 0
        nodes_added = 0
        nodes_skipped = 0
        
        # Process models
        for model in manifest.get('models', []):
            url = model.get('url')
            if not url:
                continue
            
            # Create unique key for duplicate detection
            key = url.lower()
            
            if key in self.seen_models:
                models_skipped += 1
                print(f"  ⚠ Duplicate model skipped: {model.get('name', 'Unknown')} (already in {self.seen_models[key]})")
            else:
                self.models.append(model)
                self.seen_models[key] = source
                models_added += 1
        
        # Process custom nodes
        for node in manifest.get('custom_nodes', []):
            repo = node.get('repo')
            if not repo:
                continue
            
            # Create unique key for duplicate detection
            key = repo.lower()
            
            if key in self.seen_nodes:
                nodes_skipped += 1
                print(f"  ⚠ Duplicate node skipped: {node.get('name', 'Unknown')} (already in {self.seen_nodes[key]})")
            else:
                self.custom_nodes.append(node)
                self.seen_nodes[key] = source
                nodes_added += 1
        
        return models_added, models_skipped, nodes_added, nodes_skipped
    
    def load_manifests(self, sources: List[str]) -> None:
        """Load and combine multiple manifests."""
        print(f"\n{'='*70}")
        print(f"Loading {len(sources)} manifest(s)...")
        print(f"{'='*70}\n")
        
        total_models = 0
        total_models_skipped = 0
        total_nodes = 0
        total_nodes_skipped = 0
        
        for i, source in enumerate(sources, 1):
            print(f"\n[{i}/{len(sources)}] {source}")
            manifest = self.load_manifest(source)
            
            if manifest:
                m_added, m_skipped, n_added, n_skipped = self.add_manifest(manifest, source)
                print(f"  ✓ Added: {m_added} models, {n_added} custom nodes")
                if m_skipped > 0 or n_skipped > 0:
                    print(f"  ⚠ Skipped duplicates: {m_skipped} models, {n_skipped} custom nodes")
                
                total_models += m_added
                total_models_skipped += m_skipped
                total_nodes += n_added
                total_nodes_skipped += n_skipped
            else:
                print(f"  ✗ Failed to load manifest")
        
        print(f"\n{'='*70}")
        print(f"Combined manifest summary:")
        print(f"  Models: {total_models} unique (skipped {total_models_skipped} duplicates)")
        print(f"  Custom Nodes: {total_nodes} unique (skipped {total_nodes_skipped} duplicates)")
        print(f"{'='*70}\n")
    
    def get_combined_manifest(self) -> Dict:
        """Return the combined manifest."""
        return {
            'models': self.models,
            'custom_nodes': self.custom_nodes
        }


def download_file(url: str, dest_path: Path, expected_hash: Optional[str] = None) -> bool:
    """Download a file with progress bar and optional hash verification."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists
        if dest_path.exists():
            if expected_hash:
                print(f"  📄 File exists, verifying hash...")
                if verify_hash(dest_path, expected_hash):
                    print(f"  ✓ {dest_path.name} (hash verified, skipped)")
                    return True
                else:
                    print(f"  ⚠ Hash mismatch, re-downloading...")
            else:
                print(f"  ✓ {dest_path.name} (already exists, skipped)")
                return True
        
        print(f"  ⬇ Downloading: {dest_path.name}")
        
        # Handle different URL schemes (direct download vs HTML pages)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, stream=True, timeout=30, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=f"    ",
            leave=False
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)
        
        # Verify hash if provided
        if expected_hash:
            print(f"  🔍 Verifying hash...")
            if not verify_hash(dest_path, expected_hash):
                print(f"  ✗ Hash verification failed for {dest_path.name}")
                dest_path.unlink()
                return False
        
        print(f"  ✓ Downloaded: {dest_path.name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error downloading {url}: {str(e)}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def verify_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash


def clone_repo(repo_url: str, dest_path: Path) -> bool:
    """Clone a git repository."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if dest_path.exists():
            print(f"  ✓ Repository already exists: {dest_path.name}")
            return True
        
        print(f"  📦 Cloning repository...")
        result = os.system(f"git clone --quiet {repo_url} {dest_path}")
        
        if result == 0:
            print(f"  ✓ Cloned: {dest_path.name}")
            return True
        else:
            print(f"  ✗ Failed to clone repository")
            return False
        
    except Exception as e:
        print(f"  ✗ Error cloning {repo_url}: {str(e)}")
        return False


def download_models(manifest: Dict, types_filter: Optional[List[str]] = None, dry_run: bool = False) -> tuple:
    """Download all models from manifest."""
    models = manifest.get('models', [])
    
    if types_filter:
        models = [m for m in models if m.get('type') in types_filter]
    
    print(f"\n{'='*70}")
    print(f"{'DRY RUN: ' if dry_run else ''}Downloading {len(models)} model(s)...")
    print(f"{'='*70}\n")
    
    if not models:
        print("No models to download")
        return 0, 0
    
    success_count = 0
    fail_count = 0
    
    for i, model in enumerate(models, 1):
        name = model.get('name', 'Unknown')
        url = model.get('url')
        rel_path = model.get('path', 'models/checkpoints')
        expected_hash = model.get('sha256')
        model_type = model.get('type', 'unknown')
        
        print(f"\n[{i}/{len(models)}] [{model_type}] {name}")
        
        if not url:
            print(f"  ✗ No URL provided")
            fail_count += 1
            continue
        
        if dry_run:
            print(f"  → Would download to: {rel_path}/")
            print(f"  → URL: {url}")
            success_count += 1
            continue
        
        # Determine filename from URL or model name
        filename = model.get('filename')
        if not filename:
            filename = os.path.basename(urlparse(url).path)
        
        if not filename or filename == '':
            filename = f"{name.replace(' ', '_')}.safetensors"
        
        dest_path = Path(COMFYUI_PATH) / rel_path / filename
        
        if download_file(url, dest_path, expected_hash):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*70}")
    print(f"{'DRY RUN: ' if dry_run else ''}Download complete: {success_count} succeeded, {fail_count} failed")
    print(f"{'='*70}\n")
    
    return success_count, fail_count


def install_custom_nodes(manifest: Dict, dry_run: bool = False) -> tuple:
    """Install custom nodes from manifest."""
    nodes = manifest.get('custom_nodes', [])
    
    print(f"\n{'='*70}")
    print(f"{'DRY RUN: ' if dry_run else ''}Installing {len(nodes)} custom node(s)...")
    print(f"{'='*70}\n")
    
    if not nodes:
        print("No custom nodes to install")
        return 0, 0
    
    success_count = 0
    fail_count = 0
    
    for i, node in enumerate(nodes, 1):
        name = node.get('name', 'Unknown')
        repo = node.get('repo')
        rel_path = node.get('path', 'custom_nodes')
        
        print(f"\n[{i}/{len(nodes)}] {name}")
        
        if not repo:
            print(f"  ✗ No repository URL provided")
            fail_count += 1
            continue
        
        if dry_run:
            print(f"  → Would clone to: {rel_path}/")
            print(f"  → Repo: {repo}")
            success_count += 1
            continue
        
        # Use name from manifest for directory, sanitize it
        dir_name = name.replace(' ', '-').replace('/', '-')
        dest_path = Path(COMFYUI_PATH) / rel_path / dir_name
        
        if clone_repo(repo, dest_path):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*70}")
    print(f"{'DRY RUN: ' if dry_run else ''}Custom nodes installation complete: {success_count} succeeded, {fail_count} failed")
    print(f"{'='*70}\n")
    
    return success_count, fail_count


def list_manifest_contents(manifest: Dict) -> None:
    """List all contents of the combined manifest."""
    models = manifest.get('models', [])
    nodes = manifest.get('custom_nodes', [])
    
    print(f"\n{'='*70}")
    print(f"Manifest Contents")
    print(f"{'='*70}\n")
    
    if models:
        print(f"📦 Models ({len(models)}):\n")
        
        # Group by type
        by_type = defaultdict(list)
        for model in models:
            by_type[model.get('type', 'unknown')].append(model)
        
        for model_type, type_models in sorted(by_type.items()):
            print(f"  {model_type.upper()}:")
            for model in type_models:
                name = model.get('name', 'Unknown')
                path = model.get('path', 'N/A')
                print(f"    • {name}")
                print(f"      └─ Path: {path}/")
            print()
    
    if nodes:
        print(f"🔌 Custom Nodes ({len(nodes)}):\n")
        for node in nodes:
            name = node.get('name', 'Unknown')
            repo = node.get('repo', 'N/A')
            print(f"  • {name}")
            print(f"    └─ Repo: {repo}")
        print()
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Download ComfyUI models from one or more manifest files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download from single manifest (GitHub raw URL)
  %(prog)s https://raw.githubusercontent.com/user/repo/main/manifest.json
  
  # Download from multiple manifests (combines and deduplicates)
  %(prog)s manifest1.json https://example.com/manifest2.json
  
  # List what would be downloaded without downloading
  %(prog)s --list manifest.json
  
  # Download only specific model types
  %(prog)s --types checkpoint lora manifest.json
  
  # Dry run to see what would be downloaded
  %(prog)s --dry-run manifest.json
  
  # Skip custom nodes, only download models
  %(prog)s --models-only manifest.json
        """
    )
    
    parser.add_argument('manifests', nargs='+', 
                       help='URLs or paths to manifest files (can specify multiple)')
    parser.add_argument('--types', nargs='+', 
                       choices=['checkpoint', 'vae', 'lora', 'controlnet', 'upscale', 'embeddings', 'clip'],
                       help='Only download specific model types')
    parser.add_argument('--models-only', action='store_true',
                       help='Download only models, skip custom nodes')
    parser.add_argument('--nodes-only', action='store_true',
                       help='Install only custom nodes, skip models')
    parser.add_argument('--list', action='store_true',
                       help='List all items in manifest(s) without downloading')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be downloaded without actually downloading')
    
    args = parser.parse_args()
    
    # Validate conflicting arguments
    if args.models_only and args.nodes_only:
        parser.error("Cannot use --models-only and --nodes-only together")
    
    print(f"\n{'='*70}")
    print(f"ComfyUI Model Downloader")
    print(f"{'='*70}")
    print(f"ComfyUI Path: {COMFYUI_PATH}")
    print(f"Manifests: {len(args.manifests)}")
    print(f"{'='*70}")
    
    # Load and combine manifests
    manifest_loader = ModelManifest()
    manifest_loader.load_manifests(args.manifests)
    combined_manifest = manifest_loader.get_combined_manifest()
    
    # List mode - just show contents
    if args.list:
        list_manifest_contents(combined_manifest)
        return
    
    # Download/install based on options
    total_success = 0
    total_fail = 0
    
    if not args.nodes_only:
        success, fail = download_models(combined_manifest, args.types, args.dry_run)
        total_success += success
        total_fail += fail
    
    if not args.models_only:
        success, fail = install_custom_nodes(combined_manifest, args.dry_run)
        total_success += success
        total_fail += fail
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"{'DRY RUN ' if args.dry_run else ''}SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Succeeded: {total_success}")
    print(f"✗ Failed: {total_fail}")
    print(f"{'='*70}\n")
    
    if not args.dry_run and total_success > 0:
        print("💡 Tip: Restart ComfyUI to use new models and custom nodes\n")
    
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
