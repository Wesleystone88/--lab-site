#!/usr/bin/env python3
"""
νόησις Seed Generator
Tamper-evident identity for artifacts (spine-v1)
"""

import hashlib
import json
import re
import yaml
from pathlib import Path
from datetime import datetime


class ArtifactSeeder:
    """Generate and verify seeds for νόησις artifacts"""
    
    SEED_ALGO = "sha256-v1"
    SEED_SCOPE = "spine-v1"
    
    # Spine definitions per mode
    SPINE_DEFINITIONS = {
        'ENGINEERING': [
            'card.id',
            'card.name',
            'card.namespace',
            'card.mode',
            'card.deck_mode',
            'dependencies',
            'gate',
            'ordering'
        ],
        'EXPLORATION': [
            'card.id',
            'card.name',
            'card.namespace',
            'card.mode',
            'suggested_patterns.often_paired_with',
            'suggested_patterns.helpful_for',
            'state_schema'
        ]
    }
    
    def get_nested_value(self, obj, path):
        """Get nested dict value by dot-notation path"""
        parts = path.split('.')
        value = obj
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
            if value is None:
                return None
        return value
    
    def extract_spine(self, card_file):
        """Extract spine fields from card YAML front matter"""
        with open(card_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML front matter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"No YAML front matter in {card_file}")
        
        metadata = yaml.safe_load(yaml_match.group(1))
        
        # Get mode
        mode = metadata.get('card', {}).get('mode', 'UNKNOWN')
        if mode not in self.SPINE_DEFINITIONS:
            raise ValueError(f"Unknown mode: {mode}")
        
        # Extract spine fields
        spine_fields = self.SPINE_DEFINITIONS[mode]
        spine = {}
        
        for field_path in spine_fields:
            value = self.get_nested_value(metadata, field_path)
            if value is not None:
                spine[field_path] = value
        
        return spine, mode, metadata
    
    def canonicalize_spine(self, spine):
        """Convert spine to canonical JSON form"""
        
        def sort_recursive(obj):
            """Sort all dict keys recursively"""
            if isinstance(obj, dict):
                return {k: sort_recursive(v) for k, v in sorted(obj.items())}
            elif isinstance(obj, list):
                return [sort_recursive(item) for item in obj]
            else:
                return obj
        
        sorted_spine = sort_recursive(spine)
        
        # Canonical JSON: no whitespace, sorted keys
        canonical = json.dumps(sorted_spine, sort_keys=True, separators=(',', ':'))
        
        return canonical
    
    def compute_seed(self, canonical_spine):
        """Compute SHA-256 hash of canonical spine"""
        spine_bytes = canonical_spine.encode('utf-8')
        return hashlib.sha256(spine_bytes).hexdigest()
    
    def generate_seed_identity(self, card_file, parent_seed=None):
        """Generate seed identity block for artifact"""
        spine, mode, metadata = self.extract_spine(card_file)
        canonical = self.canonicalize_spine(spine)
        seed = self.compute_seed(canonical)
        
        card_id = metadata.get('card', {}).get('id', 'UNKNOWN')
        
        identity = {
            'artifact_id': card_id,
            'seed_algo': self.SEED_ALGO,
            'seed': seed,
            'seed_scope': self.SEED_SCOPE,
            'seeded_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'locked'
        }
        
        if parent_seed:
            identity['parent_seed'] = parent_seed
        
        return identity, spine, canonical, seed
    
    def add_seed_to_card(self, card_file, parent_seed=None):
        """Add seed_identity to card YAML front matter"""
        with open(card_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse structure
        yaml_match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)(.*)', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"Invalid card format: {card_file}")
        
        yaml_start = yaml_match.group(1)
        yaml_content = yaml_match.group(2)
        yaml_end = yaml_match.group(3)
        body_content = yaml_match.group(4)
        
        # Parse existing metadata
        metadata = yaml.safe_load(yaml_content)
        
        # Generate seed identity
        identity, spine, canonical, seed = self.generate_seed_identity(card_file, parent_seed)
        
        # Add to metadata (preserve order - seed_identity first)
        new_metadata = {'seed_identity': identity}
        new_metadata.update(metadata)
        
        # Serialize to YAML
        new_yaml = yaml.dump(new_metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Reconstruct file
        new_content = yaml_start + new_yaml + yaml_end + body_content
        
        # Write back
        with open(card_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return seed, spine, canonical
    
    def verify_seed(self, card_file):
        """Verify seed matches current spine"""
        with open(card_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            return False, "No YAML front matter"
        
        metadata = yaml.safe_load(yaml_match.group(1))
        
        # Check for seed_identity
        identity = metadata.get('seed_identity')
        if not identity:
            return False, "No seed_identity found"
        
        stored_seed = identity.get('seed')
        if not stored_seed:
            return False, "No seed value"
        
        # Recompute seed from current spine
        spine, mode, _ = self.extract_spine(card_file)
        canonical = self.canonicalize_spine(spine)
        computed_seed = self.compute_seed(canonical)
        
        if stored_seed == computed_seed:
            return True, f"Seed verified (status: {identity.get('status', 'unknown')})"
        else:
            return False, f"Seed mismatch\n  Stored:   {stored_seed[:16]}...\n  Computed: {computed_seed[:16]}..."


def main():
    import sys
    import argparse
    
    # Fix Windows console encoding
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parser = argparse.ArgumentParser(description='νόησις Seed Generator (spine-v1)')
    parser.add_argument('command', choices=['generate', 'verify', 'show-spine', 'batch-generate'])
    parser.add_argument('path', help='Card file or directory path')
    parser.add_argument('--parent-seed', help='Parent seed for lineage')
    
    args = parser.parse_args()
    
    seeder = ArtifactSeeder()
    path = Path(args.path)
    
    if args.command == 'generate':
        if not path.is_file():
            print(f"Error: {path} not found")
            return 1
        
        print(f"Generating seed for: {path.name}")
        print(f"Algorithm: {seeder.SEED_ALGO}")
        print(f"Scope: {seeder.SEED_SCOPE}\n")
        
        seed, spine, canonical = seeder.add_seed_to_card(path, args.parent_seed)
        
        print(f"✅ Seed generated: {seed}\n")
        print("Spine fingerprint:")
        for key in sorted(spine.keys()):
            value = spine[key]
            if isinstance(value, (list, dict)):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nCanonical form: {canonical[:80]}...")
        print(f"\nCard updated: {path}")
        
        return 0
    
    elif args.command == 'verify':
        if not path.is_file():
            print(f"Error: {path} not found")
            return 1
        
        print(f"Verifying: {path.name}\n")
        
        valid, message = seeder.verify_seed(path)
        
        if valid:
            print(f"✅ {message}")
            return 0
        else:
            print(f"❌ {message}")
            return 1
    
    elif args.command == 'show-spine':
        if not path.is_file():
            print(f"Error: {path} not found")
            return 1
        
        spine, mode, metadata = seeder.extract_spine(path)
        canonical = seeder.canonicalize_spine(spine)
        seed = seeder.compute_seed(canonical)
        
        card_id = metadata.get('card', {}).get('id', 'UNKNOWN')
        
        print(f"Artifact: {path.name}")
        print(f"Card ID: {card_id}")
        print(f"Mode: {mode}")
        print(f"\nSpine fields ({len(spine)}):")
        for key in sorted(spine.keys()):
            value = spine[key]
            print(f"  {key}:")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"    {value}")
            else:
                print(f"    {value}")
        
        print(f"\nCanonical JSON:")
        print(f"  {canonical}")
        
        print(f"\nComputed seed (SHA-256):")
        print(f"  {seed}")
        
        return 0
    
    elif args.command == 'batch-generate':
        if not path.is_dir():
            print(f"Error: {path} is not a directory")
            return 1
        
        cards = list(path.glob("*CARD-*.md"))
        if not cards:
            print(f"No cards found in {path}")
            return 1
        
        print(f"Batch seeding: {len(cards)} cards in {path}\n")
        print(f"Algorithm: {seeder.SEED_ALGO}")
        print(f"Scope: {seeder.SEED_SCOPE}\n")
        
        results = []
        for card_file in sorted(cards):
            try:
                seed, spine, canonical = seeder.add_seed_to_card(card_file)
                results.append((card_file.name, seed, True, None))
                print(f"✅ {card_file.name}: {seed[:16]}...")
            except Exception as e:
                results.append((card_file.name, None, False, str(e)))
                print(f"❌ {card_file.name}: {e}")
        
        # Summary
        success = sum(1 for r in results if r[2])
        print(f"\n{'='*60}")
        print(f"Batch complete: {success}/{len(results)} cards seeded")
        
        if success < len(results):
            print(f"\nFailed cards:")
            for name, seed, ok, error in results:
                if not ok:
                    print(f"  - {name}: {error}")
        
        return 0 if success == len(results) else 1


if __name__ == "__main__":
    exit(main())
