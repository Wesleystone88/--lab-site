#!/usr/bin/env python3
"""
νόησις Graph Viewer
Simple visualization tool for card graph metadata across all deck modes.
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict


class NoesisGraphViewer:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.cards = {}
        self.decks = defaultdict(list)
        
    def scan_cards(self):
        """Scan all markdown files for graph metadata"""
        
        # Scan Emergence Deck v0.1
        emergence_path = self.workspace_root / "noesis-release" / "deck" / "v0.1" / "cards"
        if emergence_path.exists():
            self._scan_directory(emergence_path, "noesis.emergence.v0.1")
        
        # Scan Canonical Deck v1.0
        canonical_path = self.workspace_root / "noesis-release" / "deck" / "v1.0" / "cards"
        if canonical_path.exists():
            self._scan_directory(canonical_path, "noesis.canonical.v1.0")
        
        # Scan Conversation Grounding (Exploration Mode)
        exploration_path = self.workspace_root / "new" / "cards"
        if exploration_path.exists():
            self._scan_directory(exploration_path, "noesis.conversation-grounding.exploration")
    
    def _scan_directory(self, directory, expected_namespace):
        """Scan a directory for card files"""
        for card_file in directory.glob("*.md"):
            # Match any file with CARD- in the name
            if "CARD-" in card_file.name or card_file.name.startswith("0"):
                card_data = self._extract_metadata(card_file)
                if card_data:
                    namespace = card_data.get('card', {}).get('namespace', expected_namespace)
                    self.cards[card_data['id']] = card_data
                    self.decks[namespace].append(card_data)
    
    def _extract_metadata(self, filepath):
        """Extract YAML front matter from markdown file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match YAML front matter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            return None
        
        try:
            metadata = yaml.safe_load(yaml_match.group(1))
            metadata['filepath'] = str(filepath)
            metadata['id'] = metadata['card']['id']
            return metadata
        except yaml.YAMLError:
            return None
    
    def print_deck_summary(self):
        """Print overview of all decks"""
        print("=" * 80)
        print("νόησις GRAPH VIEWER — Deck Summary")
        print("=" * 80)
        print()
        
        for namespace, cards in sorted(self.decks.items()):
            mode = cards[0].get('card', {}).get('mode', 'UNKNOWN')
            deck_mode = cards[0].get('card', {}).get('deck_mode', '')
            
            print(f"📦 {namespace}")
            print(f"   Mode: {mode}" + (f" ({deck_mode})" if deck_mode else ""))
            print(f"   Cards: {len(cards)}")
            print()
    
    def print_card_list(self, namespace=None):
        """Print detailed card list"""
        print("=" * 80)
        print("νόησις GRAPH VIEWER — Card List")
        print("=" * 80)
        print()
        
        decks_to_show = {namespace: self.decks[namespace]} if namespace else self.decks
        
        for ns, cards in sorted(decks_to_show.items()):
            print(f"\n{'─' * 80}")
            print(f"DECK: {ns}")
            print('─' * 80)
            
            sorted_cards = sorted(cards, key=lambda c: c.get('ordering', {}).get('position', 999))
            
            for card in sorted_cards:
                card_info = card.get('card', {})
                deps = card.get('dependencies', {})
                ordering = card.get('ordering', {})
                gate = card.get('gate', {})
                
                print(f"\n  🃏 {card_info.get('id')} — {card_info.get('name')}")
                print(f"     Position: {ordering.get('position', 'N/A')}")
                
                if deps.get('upstream'):
                    print(f"     ⬆️  Upstream: {', '.join(deps['upstream'])}")
                if deps.get('downstream'):
                    print(f"     ⬇️  Downstream: {', '.join(deps['downstream'])}")
                if deps.get('feeds_into'):
                    print(f"     🔄 Feeds Into: {', '.join(deps['feeds_into'])}")
                if deps.get('required_by'):
                    print(f"     ⚠️  Required By: {', '.join(deps['required_by'])}")
                
                if gate:
                    enforcement = gate.get('enforcement', 'none')
                    blocks = gate.get('blocks_downstream', False)
                    emoji = '🚫' if blocks else '⚠️' if enforcement == 'diagnostic' else 'ℹ️'
                    print(f"     {emoji} Gate: {enforcement}" + (" (blocks)" if blocks else ""))
                
                # Exploration mode: show suggestions
                if 'suggested_patterns' in card:
                    patterns = card['suggested_patterns']
                    if patterns.get('often_paired_with'):
                        print(f"     💡 Pairs With: {', '.join(patterns['often_paired_with'])}")
                    if patterns.get('helpful_for'):
                        print(f"     🎯 Helpful For: {', '.join(patterns['helpful_for'][:2])}")
            
            print()
    
    def print_dependency_graph(self, namespace=None):
        """Print ASCII dependency graph"""
        print("=" * 80)
        print("νόησις GRAPH VIEWER — Dependency Graph")
        print("=" * 80)
        print()
        
        decks_to_show = {namespace: self.decks[namespace]} if namespace else self.decks
        
        for ns, cards in sorted(decks_to_show.items()):
            print(f"\n{'─' * 80}")
            print(f"DECK: {ns}")
            mode = cards[0].get('card', {}).get('mode', 'UNKNOWN')
            print(f"MODE: {mode}")
            print('─' * 80)
            print()
            
            sorted_cards = sorted(cards, key=lambda c: c.get('ordering', {}).get('position', 999))
            
            for card in sorted_cards:
                card_info = card.get('card', {})
                deps = card.get('dependencies', {})
                gate = card.get('gate', {})
                
                # Card representation
                card_id = card_info.get('id', 'UNKNOWN')
                gate_emoji = '🚫' if gate.get('blocks_downstream') else '⚠️' if gate.get('enforcement') == 'diagnostic' else '○'
                
                print(f"{gate_emoji} {card_id}: {card_info.get('name', 'Unnamed')}")
                
                # Show dependencies
                if deps.get('upstream'):
                    for upstream in deps['upstream']:
                        print(f"    ↑ requires {upstream}")
                
                if deps.get('downstream'):
                    for downstream in deps['downstream']:
                        print(f"    ↓ enables {downstream}")
                
                print()
    
    def validate_graph(self):
        """Validate graph integrity"""
        print("=" * 80)
        print("νόησις GRAPH VIEWER — Graph Validation")
        print("=" * 80)
        print()
        
        errors = []
        warnings = []
        
        for namespace, cards in self.decks.items():
            mode = cards[0].get('card', {}).get('mode', 'UNKNOWN')
            
            print(f"Validating: {namespace} ({mode})")
            print()
            
            card_ids = {c['id'] for c in cards}
            
            for card in cards:
                card_id = card['id']
                deps = card.get('dependencies', {})
                
                # Check upstream references
                for upstream in deps.get('upstream', []):
                    if upstream not in card_ids:
                        errors.append(f"  ❌ {card_id}: upstream '{upstream}' not found in deck")
                
                # Check downstream references
                for downstream in deps.get('downstream', []):
                    if downstream not in card_ids:
                        errors.append(f"  ❌ {card_id}: downstream '{downstream}' not found in deck")
                
                # Engineering mode: check ordering consistency
                if mode == 'ENGINEERING':
                    ordering = card.get('ordering', {})
                    position = ordering.get('position')
                    
                    if position is None:
                        warnings.append(f"  ⚠️  {card_id}: no position defined")
                    
                    # Check required_after
                    for required_after in ordering.get('required_after', []):
                        if required_after not in card_ids:
                            errors.append(f"  ❌ {card_id}: required_after '{required_after}' not found")
            
            if not errors and not warnings:
                print("  ✅ All checks passed")
            
            print()
        
        if errors:
            print("\n🚨 ERRORS:")
            for error in errors:
                print(error)
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(warning)
        
        if not errors and not warnings:
            print("✅ Graph validation complete: No issues found")
        
        print()
    
    def export_dot(self, output_file=None, namespace=None):
        """Export graph as DOT format for Graphviz"""
        if output_file is None:
            output_file = self.workspace_root / "noesis-graph.dot"
        
        decks_to_export = {namespace: self.decks[namespace]} if namespace else self.decks
        
        dot_lines = ["digraph noesis_graph {"]
        dot_lines.append("  rankdir=TB;")
        dot_lines.append("  node [shape=box, style=rounded];")
        dot_lines.append("")
        
        for ns, cards in sorted(decks_to_export.items()):
            # Create subgraph for each deck
            subgraph_name = ns.replace('.', '_').replace('-', '_')
            mode = cards[0].get('card', {}).get('mode', 'UNKNOWN')
            
            dot_lines.append(f"  subgraph cluster_{subgraph_name} {{")
            dot_lines.append(f'    label="{ns}\\n({mode})";')
            
            # Node colors based on mode
            if mode == "ENGINEERING":
                enforcement = cards[0].get('gate', {}).get('enforcement', 'none')
                if enforcement == 'strict':
                    dot_lines.append('    node [fillcolor=lightcoral, style="rounded,filled"];')
                else:
                    dot_lines.append('    node [fillcolor=lightblue, style="rounded,filled"];')
            else:
                dot_lines.append('    node [fillcolor=lightgreen, style="rounded,filled"];')
            
            # Define nodes
            for card in cards:
                card_id = card['id'].replace('-', '_')
                card_name = card.get('card', {}).get('name', 'Unnamed')
                dot_lines.append(f'    {card_id} [label="{card["id"]}\\n{card_name}"];')
            
            dot_lines.append("  }")
            dot_lines.append("")
        
        # Define edges
        for ns, cards in sorted(decks_to_export.items()):
            for card in cards:
                card_id = card['id'].replace('-', '_')
                deps = card.get('dependencies', {})
                
                # Upstream dependencies
                for upstream in deps.get('upstream', []):
                    upstream_id = upstream.replace('-', '_')
                    dot_lines.append(f"  {upstream_id} -> {card_id};")
                
                # Feeds into (dashed)
                for feeds in deps.get('feeds_into', []):
                    feeds_id = feeds.replace('-', '_')
                    dot_lines.append(f"  {card_id} -> {feeds_id} [style=dashed, color=gray];")
        
        dot_lines.append("}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_lines))
        
        print(f"✅ Exported DOT graph to: {output_file}")
        print(f"   To visualize: dot -Tpng {output_file} -o noesis-graph.png")
        print()


def main():
    import sys
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Detect workspace root
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = os.getcwd()
    
    print(f"Scanning workspace: {workspace}\n")
    
    viewer = NoesisGraphViewer(workspace)
    viewer.scan_cards()
    
    # Print all views
    viewer.print_deck_summary()
    viewer.print_card_list()
    viewer.print_dependency_graph()
    viewer.validate_graph()
    viewer.export_dot()


if __name__ == "__main__":
    main()
