#!/usr/bin/env python3
"""
ComfyUI Model Downloader (Portable Version)
Downloads models to the models directory from one or more manifest files.
Supports duplicate detection and manifest combining.
Uses curl for performance, falls back to requests for compatibility.
No tqdm dependency - uses native progress bars.
"""

import os
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urlparse
import argparse
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

# Try to import requests for manifest fetching and fallback downloads
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  Warning: 'requests' not installed. Will use curl for everything.")

COMFYUI_PATH = os.environ.get('COMFYUI_PATH', '/app/ComfyUI')


def has_curl() -> bool:
    """Check if curl is available."""
    return shutil.which('curl') is not None


class ModelManifest:
    """Handles loading, combining, and deduplicating model manifests."""
    
    def __init__(self):
        self.models = []
        self.seen_models = {}  # Track by URL to detect duplicates
    
    def load_manifest(self, source: str) -> Optional[Dict]:
        """Load manifest from URL or local file."""
        try:
            if source.startswith('http://') or source.startswith('https://'):
                print(f"📥 Fetching manifest from: {source}")
                
                # Try curl first, then requests
                if has_curl():
                    return self._load_manifest_curl(source)
                elif HAS_REQUESTS:
                    return self._load_manifest_requests(source)
                else:
                    print(f"✗ No method available to fetch remote manifest")
                    return None
            else:
                print(f"📂 Loading manifest from: {source}")
                with open(source, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"✗ Error loading manifest from {source}: {str(e)}")
            return None
    
    def _load_manifest_curl(self, url: str) -> Optional[Dict]:
        """Load manifest using curl."""
        try:
            result = subprocess.run(
                ['curl', '-sS', '-L', '--max-time', '30', url],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"✗ curl failed: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {str(e)}")
            return None
    
    def _load_manifest_requests(self, url: str) -> Optional[Dict]:
        """Load manifest using requests."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ requests failed: {str(e)}")
            return None
    
    def add_manifest(self, manifest: Dict, source: str) -> Tuple[int, int]:
        """Add a manifest, tracking duplicates."""
        if not manifest:
            return 0, 0
        
        models_added = 0
        models_skipped = 0
        
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
        
        return models_added, models_skipped
    
    def load_manifests(self, sources: List[str]) -> None:
        """Load and combine multiple manifests."""
        print(f"\n{'='*70}")
        print(f"Loading {len(sources)} manifest(s)...")
        print(f"{'='*70}\n")
        
        total_models = 0
        total_models_skipped = 0
        
        for i, source in enumerate(sources, 1):
            print(f"\n[{i}/{len(sources)}] {source}")
            manifest = self.load_manifest(source)
            
            if manifest:
                m_added, m_skipped = self.add_manifest(manifest, source)
                print(f"  ✓ Added: {m_added} models")
                if m_skipped > 0:
                    print(f"  ⚠ Skipped duplicates: {m_skipped} models")
                
                total_models += m_added
                total_models_skipped += m_skipped
            else:
                print(f"  ✗ Failed to load manifest")
        
        print(f"\n{'='*70}")
        print(f"Combined manifest summary:")
        print(f"  Models: {total_models} unique (skipped {total_models_skipped} duplicates)")
        print(f"{'='*70}\n")
    
    def get_combined_manifest(self) -> Dict:
        """Return the combined manifest."""
        return {
            'models': self.models
        }


def download_with_curl(url: str, dest_path: Path) -> bool:
    """Download file using curl with progress bar."""
    try:
        cmd = [
            'curl',
            '-L',                    # Follow redirects
            '-o', str(dest_path),    # Output file
            '-#',                    # Progress bar (simple)
            '--create-dirs',         # Create parent directories
            '-C', '-',               # Resume if interrupted
            '--max-time', '3600',    # 1 hour timeout
            '--connect-timeout', '30',  # Connection timeout
            url
        ]
        
        # Run curl and show its output directly
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ curl failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def download_with_requests(url: str, dest_path: Path) -> bool:
    """Download file using requests with ASCII progress bar."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, stream=True, timeout=30, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show ASCII progress bar
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_down = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        bar_length = 40
                        filled = int(bar_length * downloaded / total_size)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f'\r    [{bar}] {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f} MB)', 
                              end='', flush=True)
        
        if total_size > 0:
            print()  # New line after progress
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def download_file(url: str, dest_path: Path, expected_hash: Optional[str] = None) -> bool:
    """Download a file using the best available method."""
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
                dest_path.unlink()
        else:
            print(f"  ✓ {dest_path.name} (already exists, skipped)")
            return True
    
    print(f"  ⬇ Downloading: {dest_path.name}")
    
    # Detect available download tools
    curl_available = has_curl()
    
    success = False
    
    # Try methods in order of preference
    if curl_available:
        print(f"    Using: curl")
        success = download_with_curl(url, dest_path)
    elif HAS_REQUESTS:
        print(f"    Using: Python requests")
        success = download_with_requests(url, dest_path)
    else:
        print(f"  ✗ No download method available (need curl or requests)")
        return False
    
    if not success:
        if dest_path.exists():
            dest_path.unlink()
        return False
    
    # Verify hash if provided
    if expected_hash:
        print(f"  🔍 Verifying hash...")
        if not verify_hash(dest_path, expected_hash):
            print(f"  ✗ Hash verification failed")
            dest_path.unlink()
            return False
    
    print(f"  ✓ Downloaded: {dest_path.name}")
    return True


def verify_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash


def download_models(manifest: Dict, types_filter: Optional[List[str]] = None, dry_run: bool = False) -> Tuple[int, int]:
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


def list_manifest_contents(manifest: Dict) -> None:
    """List all contents of the combined manifest."""
    models = manifest.get('models', [])
    
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
    else:
        print("No models found in manifest(s)")
    
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Download ComfyUI models from one or more manifest files (Portable Version)',
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
  %(prog)s --types checkpoints loras manifest.json
  
  # Dry run to see what would be downloaded
  %(prog)s --dry-run manifest.json

Download Method Priority:
  1. curl (preferred) - Best performance, native progress bar
  2. requests (fallback) - Universal compatibility, ASCII progress bar
  
This version requires NO tqdm dependency!
        """
    )
    
    parser.add_argument('manifests', nargs='+', 
                       help='URLs or paths to manifest files (can specify multiple)')
    parser.add_argument('--types', nargs='+', 
                       choices=['audio_encoders', 'checkpoints', 'clip', 'clip_vision', 'configs', 
                                'controlnet', 'diffusers', 'diffusion_models', 'embeddings', 'gligen',
                                'hypernetworks', 'loras', 'model_patches', 'photomaker', 'style_models',
                                'text_encoders', 'unet', 'upscale_models', 'vae', 'vae_approx'],
                       help='Only download specific model types')
    parser.add_argument('--list', action='store_true',
                       help='List all items in manifest(s) without downloading')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be downloaded without actually downloading')
    
    args = parser.parse_args()
    
    # Check available tools
    curl_available = has_curl()
    
    print(f"\n{'='*70}")
    print(f"ComfyUI Model Downloader (Portable Version)")
    print(f"{'='*70}")
    print(f"ComfyUI Path: {COMFYUI_PATH}")
    print(f"Manifests: {len(args.manifests)}")
    print(f"Download method: ", end='')
    if curl_available:
        print('curl (native progress bar)')
    elif HAS_REQUESTS:
        print('requests (ASCII progress bar)')
    else:
        print('NONE - installation required!')
    print(f"{'='*70}")
    
    # Load and combine manifests
    manifest_loader = ModelManifest()
    manifest_loader.load_manifests(args.manifests)
    combined_manifest = manifest_loader.get_combined_manifest()
    
    # List mode - just show contents
    if args.list:
        list_manifest_contents(combined_manifest)
        return
    
    # Download models
    total_success, total_fail = download_models(combined_manifest, args.types, args.dry_run)
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"{'DRY RUN ' if args.dry_run else ''}SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Succeeded: {total_success}")
    print(f"✗ Failed: {total_fail}")
    print(f"{'='*70}\n")
    
    if not args.dry_run and total_success > 0:
        print("💡 Tip: Restart ComfyUI to use new models\n")
    
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == '__main__':
    main()
