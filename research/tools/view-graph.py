#!/usr/bin/env python3
"""
Noesis Graph Viewer - Simple ASCII version for Windows
View card relationships across all deck modes
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict


def scan_cards(workspace_root):
    """Scan all card files for graph metadata"""
    cards = {}
    decks = defaultdict(list)
    
    # Scan locations
    locations = [
        (Path(workspace_root) / "noesis-release" / "deck" / "v0.1" / "cards", "emergence"),
        (Path(workspace_root) / "noesis-release" / "deck" / "v1.0" / "cards", "canonical"),
        (Path(workspace_root) / "new" / "cards", "exploration"),
    ]
    
    for directory, deck_type in locations:
        if not directory.exists():
            continue
            
        for card_file in directory.glob("*.md"):
            if "CARD-" not in card_file.name:
                continue
                
            with open(card_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract YAML front matter
            yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not yaml_match:
                continue
                
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
                card_info = metadata.get('card', {})
                card_id = card_info.get('id', 'UNKNOWN')
                
                cards[card_id] = {
                    'id': card_id,
                    'name': card_info.get('name', 'Unnamed'),
                    'namespace': card_info.get('namespace', ''),
                    'mode': card_info.get('mode', 'UNKNOWN'),
                    'deck_mode': card_info.get('deck_mode', ''),
                    'deps': metadata.get('dependencies', {}),
                    'gate': metadata.get('gate', {}),
                    'ordering': metadata.get('ordering', {}),
                    'suggestions': metadata.get('suggested_patterns', {}),
                    'file': str(card_file.name)
                }
                
                decks[deck_type].append(cards[card_id])
            except:
                pass
    
    return cards, decks


def print_summary(decks):
    """Print deck summary"""
    print("\n" + "=" * 80)
    print("NOESIS GRAPH VIEWER - Deck Summary")
    print("=" * 80)
    
    for deck_type, cards in sorted(decks.items()):
        if not cards:
            continue
        mode = cards[0]['mode']
        deck_mode = cards[0]['deck_mode']
        namespace = cards[0]['namespace']
        
        print(f"\n{deck_type.upper()}")
        print(f"  Namespace: {namespace}")
        print(f"  Mode: {mode}" + (f" ({deck_mode})" if deck_mode else ""))
        print(f"  Cards: {len(cards)}")


def print_card_details(decks):
    """Print detailed card information"""
    print("\n" + "=" * 80)
    print("NOESIS GRAPH VIEWER - Card Details")
    print("=" * 80)
    
    for deck_type, cards in sorted(decks.items()):
        if not cards:
            continue
            
        print(f"\n{'-' * 80}")
        print(f"DECK: {deck_type.upper()}")
        print('-' * 80)
        
        sorted_cards = sorted(cards, key=lambda c: c['ordering'].get('position', 999))
        
        for card in sorted_cards:
            print(f"\n  [{card['id']}] {card['name']}")
            print(f"    Position: {card['ordering'].get('position', 'N/A')}")
            
            deps = card['deps']
            if deps.get('upstream'):
                print(f"    Upstream: {', '.join(deps['upstream'])}")
            if deps.get('downstream'):
                print(f"    Downstream: {', '.join(deps['downstream'])}")
            if deps.get('feeds_into'):
                print(f"    Feeds Into: {', '.join(deps['feeds_into'])}")
            
            gate = card['gate']
            if gate:
                enforcement = gate.get('enforcement', 'none')
                blocks = " (BLOCKS)" if gate.get('blocks_downstream') else ""
                print(f"    Gate: {enforcement}{blocks}")
            
            # Exploration mode suggestions
            if card['suggestions']:
                patterns = card['suggestions']
                if patterns.get('often_paired_with'):
                    print(f"    Pairs With: {', '.join(patterns['often_paired_with'][:3])}")


def print_dependency_tree(decks):
    """Print dependency tree"""
    print("\n" + "=" * 80)
    print("NOESIS GRAPH VIEWER - Dependency Tree")
    print("=" * 80)
    
    for deck_type, cards in sorted(decks.items()):
        if not cards:
            continue
            
        print(f"\n{'-' * 80}")
        print(f"DECK: {deck_type.upper()} ({cards[0]['mode']})")
        print('-' * 80)
        
        sorted_cards = sorted(cards, key=lambda c: c['ordering'].get('position', 999))
        
        for card in sorted_cards:
            gate_marker = "[STRICT]" if card['gate'].get('enforcement') == 'strict' else \
                         "[DIAG]" if card['gate'].get('enforcement') == 'diagnostic' else ""
            
            print(f"\n  {gate_marker} {card['id']}: {card['name']}")
            
            deps = card['deps']
            for upstream in deps.get('upstream', []):
                print(f"      ^ requires {upstream}")
            for downstream in deps.get('downstream', []):
                print(f"      v enables {downstream}")


def validate_graph(cards, decks):
    """Validate graph integrity"""
    print("\n" + "=" * 80)
    print("NOESIS GRAPH VIEWER - Validation")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    for deck_type, deck_cards in decks.items():
        if not deck_cards:
            continue
            
        print(f"\nValidating {deck_type}...")
        
        deck_ids = {c['id'] for c in deck_cards}
        
        for card in deck_cards:
            deps = card['deps']
            
            # Check upstream references
            for upstream in deps.get('upstream', []):
                if upstream not in deck_ids:
                    errors.append(f"  ERROR: {card['id']} -> upstream '{upstream}' not found")
            
            # Check downstream references
            for downstream in deps.get('downstream', []):
                if downstream not in deck_ids:
                    errors.append(f"  ERROR: {card['id']} -> downstream '{downstream}' not found")
            
            # Engineering mode checks
            if card['mode'] == 'ENGINEERING':
                if card['ordering'].get('position') is None:
                    warnings.append(f"  WARNING: {card['id']} has no position")
        
        if not errors and not warnings:
            print("  OK - No issues found")
    
    if errors:
        print("\nERRORS FOUND:")
        for error in errors:
            print(error)
    
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(warning)
    
    if not errors and not warnings:
        print("\nValidation complete - All graphs valid!")
    
    return len(errors) == 0


def export_dot(cards, decks, output_file):
    """Export as DOT file for Graphviz"""
    lines = ["digraph noesis {"]
    lines.append("  rankdir=TB;")
    lines.append("  node [shape=box, style=rounded];")
    
    for deck_type, deck_cards in sorted(decks.items()):
        if not deck_cards:
            continue
            
        # Subgraph per deck
        subgraph_name = deck_type.replace('.', '_').replace('-', '_')
        lines.append(f"\n  subgraph cluster_{subgraph_name} {{")
        lines.append(f'    label="{deck_type}";')
        
        # Color by mode
        mode = deck_cards[0]['mode']
        if mode == 'ENGINEERING':
            if deck_cards[0]['gate'].get('enforcement') == 'strict':
                lines.append('    node [fillcolor=lightcoral, style="rounded,filled"];')
            else:
                lines.append('    node [fillcolor=lightblue, style="rounded,filled"];')
        else:
            lines.append('    node [fillcolor=lightgreen, style="rounded,filled"];')
        
        # Nodes
        for card in deck_cards:
            node_id = card['id'].replace('-', '_')
            lines.append(f'    {node_id} [label="{card["id"]}\\n{card["name"]}"];')
        
        lines.append("  }")
    
    # Edges
    for deck_cards in decks.values():
        for card in deck_cards:
            node_id = card['id'].replace('-', '_')
            
            for upstream in card['deps'].get('upstream', []):
                up_id = upstream.replace('-', '_')
                lines.append(f"  {up_id} -> {node_id};")
            
            for feeds in card['deps'].get('feeds_into', []):
                feed_id = feeds.replace('-', '_')
                lines.append(f"  {node_id} -> {feed_id} [style=dashed, color=gray];")
    
    lines.append("}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\nExported DOT file: {output_file}")
    print(f"To visualize: dot -Tpng {output_file} -o noesis-graph.png")


if __name__ == "__main__":
    import sys
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print(f"Scanning workspace: {workspace}")
    
    cards, decks = scan_cards(workspace)
    
    print(f"\nFound {len(cards)} total cards across {len(decks)} decks")
    
    print_summary(decks)
    print_card_details(decks)
    print_dependency_tree(decks)
    
    is_valid = validate_graph(cards, decks)
    
    dot_file = Path(workspace) / "noesis-graph.dot"
    export_dot(cards, decks, dot_file)
    
    print("\n" + "=" * 80)
    print("Graph analysis complete!")
    print("=" * 80)
