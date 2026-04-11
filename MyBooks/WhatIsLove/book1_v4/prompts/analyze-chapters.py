#!/usr/bin/env python3
"""
Analyze all chapter files in the chapters folder.
Provides per-chapter statistics and totals.
Creates HTML visualization charts.
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_chapter(filepath):
    """Analyze a single chapter file and return statistics."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract chapter title from first H1 heading
    chapter_title = "Unknown"
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            chapter_title = line[2:].strip()
            break
    
    stats = {
        'title': chapter_title,
        'lines': len(lines),
        'words': len(content.split()),
        'characters': len(content),
        'blockquotes': 0,
        'callouts': 0,
        'headings': {
            'h1': 0,
            'h2': 0,
            'h3': 0,
            'h4': 0
        },
        'scripture_refs': 0,
        'ccc_refs': 0,
        'footnotes': 0,
        'bold_text': 0,
        'italic_text': 0,
        'lists': 0,
        'horizontal_rules': 0
    }
    
    in_blockquote = False
    in_callout = False
    
    for line in lines:
        # Blockquotes - <div class="blockquote">
        if '<div class="blockquote">' in line:
            in_blockquote = True
            stats['blockquotes'] += 1
        if in_blockquote and '</div>' in line:
            in_blockquote = False
        
        # Callouts - <div class="callout" style=...>
        if '<div class="callout"' in line:
            in_callout = True
            stats['callouts'] += 1
        if in_callout and '</div>' in line:
            in_callout = False
        
        # Headings
        if line.startswith('# ') and not line.startswith('## '):
            stats['headings']['h1'] += 1
        elif line.startswith('## '):
            stats['headings']['h2'] += 1
        elif line.startswith('### '):
            stats['headings']['h3'] += 1
        elif line.startswith('#### '):
            stats['headings']['h4'] += 1
        
        # Scripture references (common patterns)
        scripture_pattern = r'\b(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)\s+\d+:\d+'
        stats['scripture_refs'] += len(re.findall(scripture_pattern, line))
        
        # CCC references
        ccc_pattern = r'\bCCC\s+\d+'
        stats['ccc_refs'] += len(re.findall(ccc_pattern, line))
        
        # Footnotes
        if re.search(r'\[\^\d+\]', line):
            stats['footnotes'] += 1
        
        # Bold text
        stats['bold_text'] += len(re.findall(r'\*\*[^*]+\*\*', line))
        
        # Italic text (excluding bold-italic)
        stats['italic_text'] += len(re.findall(r'(?<!\*)\*(?!\*)[^*]+\*(?!\*)', line))
        
        # Lists
        if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            stats['lists'] += 1
        
        # Horizontal rules
        if re.match(r'^-{3,}$', line.strip()) or re.match(r'^_{3,}$', line.strip()) or re.match(r'^\*{3,}$', line.strip()):
            stats['horizontal_rules'] += 1
    
    return stats

def format_number(num):
    """Format number with commas for readability."""
    return f"{num:,}"

def print_chapter_stats(filename, stats):
    """Print statistics for a single chapter."""
    print(f"\n{'='*70}")
    print(f"  {filename}")
    print(f"{'='*70}")
    print(f"  Lines:              {format_number(stats['lines']):>10}")
    print(f"  Words:              {format_number(stats['words']):>10}")
    print(f"  Characters:         {format_number(stats['characters']):>10}")
    print(f"  Blockquotes:        {format_number(stats['blockquotes']):>10}")
    print(f"  Callouts:           {format_number(stats['callouts']):>10}")
    print(f"  Scripture Refs:     {format_number(stats['scripture_refs']):>10}")
    print(f"  CCC References:     {format_number(stats['ccc_refs']):>10}")
    print(f"  Footnotes:          {format_number(stats['footnotes']):>10}")
    print(f"  Headings (H1):      {format_number(stats['headings']['h1']):>10}")
    print(f"  Headings (H2):      {format_number(stats['headings']['h2']):>10}")
    print(f"  Headings (H3):      {format_number(stats['headings']['h3']):>10}")
    print(f"  Bold Text:          {format_number(stats['bold_text']):>10}")
    print(f"  Italic Text:        {format_number(stats['italic_text']):>10}")
    print(f"  List Items:         {format_number(stats['lists']):>10}")
    print(f"  Horizontal Rules:   {format_number(stats['horizontal_rules']):>10}")

def main():
    """Main function to analyze all chapters."""
    chapters_dir = Path(__file__).parent / 'chapters'
    
    if not chapters_dir.exists():
        print(f"Error: chapters directory not found at {chapters_dir}")
        return
    
    # Get all markdown files in chapters directory
    chapter_files = sorted(chapters_dir.glob('*.md'))
    
    if not chapter_files:
        print(f"No markdown files found in {chapters_dir}")
        return
    
    print("\n" + "#" * 70)
    print("  CHAPTER ANALYSIS REPORT")
    print(f"  Total Files: {len(chapter_files)}")
    print("#" * 70)
    
    # Initialize totals
    totals = defaultdict(int)
    totals['headings'] = defaultdict(int)
    
    # Analyze each chapter
    for filepath in chapter_files:
        stats = analyze_chapter(filepath)
        print_chapter_stats(filepath.name, stats)
        
        # Add to totals
        for key, value in stats.items():
            if key == 'title':
                # Skip title field - it's not a numeric stat
                continue
            elif key == 'headings':
                for h_level, count in value.items():
                    totals['headings'][h_level] += count
            else:
                totals[key] += value
    
    # Print totals
    print("\n" + "=" * 70)
    print("  TOTALS ACROSS ALL CHAPTERS")
    print("=" * 70)
    print(f"  Total Files:        {format_number(len(chapter_files)):>10}")
    print(f"  Total Lines:        {format_number(totals['lines']):>10}")
    print(f"  Total Words:        {format_number(totals['words']):>10}")
    print(f"  Total Characters:   {format_number(totals['characters']):>10}")
    print(f"  Total Blockquotes:  {format_number(totals['blockquotes']):>10}")
    print(f"  Total Callouts:     {format_number(totals['callouts']):>10}")
    print(f"  Total Scripture:    {format_number(totals['scripture_refs']):>10}")
    print(f"  Total CCC Refs:     {format_number(totals['ccc_refs']):>10}")
    print(f"  Total Footnotes:    {format_number(totals['footnotes']):>10}")
    print(f"  Total H1 Headings:  {format_number(totals['headings']['h1']):>10}")
    print(f"  Total H2 Headings:  {format_number(totals['headings']['h2']):>10}")
    print(f"  Total H3 Headings:  {format_number(totals['headings']['h3']):>10}")
    print(f"  Total Bold Text:    {format_number(totals['bold_text']):>10}")
    print(f"  Total Italic Text:  {format_number(totals['italic_text']):>10}")
    print(f"  Total List Items:   {format_number(totals['lists']):>10}")
    print(f"  Total HR Lines:     {format_number(totals['horizontal_rules']):>10}")
    
    # Reading time estimates (average reading speed: 200-250 wpm, slow: 150 wpm)
    avg_reading_speed = 225  # words per minute
    slow_reading_speed = 150  # words per minute
    
    avg_minutes = totals['words'] / avg_reading_speed
    slow_minutes = totals['words'] / slow_reading_speed
    
    print("\n" + "=" * 70)
    print("  ESTIMATED READING TIME")
    print("=" * 70)
    print(f"  Average Pace (225 wpm):  {int(avg_minutes // 60):>3}h {int(avg_minutes % 60):>2}m")
    print(f"  Slow Pace (150 wpm):     {int(slow_minutes // 60):>3}h {int(slow_minutes % 60):>2}m")
    
    # Calculate averages
    num_files = len(chapter_files)
    print("\n" + "=" * 70)
    print("  AVERAGES PER CHAPTER")
    print("=" * 70)
    print(f"  Avg Lines:          {format_number(totals['lines'] // num_files):>10}")
    print(f"  Avg Words:          {format_number(totals['words'] // num_files):>10}")
    print(f"  Avg Characters:     {format_number(totals['characters'] // num_files):>10}")
    print(f"  Avg Blockquotes:    {format_number(totals['blockquotes'] // num_files):>10}")
    print(f"  Avg Callouts:       {format_number(totals['callouts'] // num_files):>10}")
    print(f"  Avg Scripture:      {format_number(totals['scripture_refs'] // num_files):>10}")
    print(f"  Avg H2 Headings:    {format_number(totals['headings']['h2'] // num_files):>10}")
    
    print("\n" + "#" * 70 + "\n")
    
    return chapter_files, totals

def create_html_charts(chapter_files, all_stats):
    """Create HTML file with interactive charts."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter Analysis Charts</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 40px;
        }
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-title {
            text-align: center;
            color: #555;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 600;
        }
        canvas {
            max-height: 400px;
        }
    </style>
</head>
<body>
    <h1>📊 Chapter Analysis - Visual Comparison</h1>
'''
    
    # Prepare data
    chapter_names = [f.stem.replace('chapter_', 'Ch ') for f in chapter_files]
    chapter_titles = [stats['title'] for stats in all_stats]
    
    # Create individual charts for each metric
    metrics = [
        ('lines', 'Lines per Chapter', '#3498db'),
        ('words', 'Words per Chapter', '#2ecc71'),
        ('characters', 'Characters per Chapter', '#9b59b6'),
        ('blockquotes', 'Blockquotes per Chapter', '#e74c3c'),
        ('callouts', 'Callouts per Chapter', '#f39c12'),
        ('scripture_refs', 'Scripture References per Chapter', '#1abc9c'),
        ('ccc_refs', 'CCC References per Chapter', '#34495e'),
        ('bold_text', 'Bold Text per Chapter', '#e67e22'),
        ('lists', 'List Items per Chapter', '#16a085'),
    ]
    
    for metric_key, title, color in metrics:
        data_values = [stats[metric_key] for stats in all_stats]
        
        html_content += f'''    <div class="chart-container">
        <div class="chart-title">{title}</div>
        <canvas id="chart_{metric_key}"></canvas>
    </div>
'''
    
    # Add JavaScript for charts
    html_content += '''    <script>
        const labels = ''' + str(chapter_names) + ''';
        const chapterTitles = ''' + str(chapter_titles) + ''';
        
        const chartConfig = {
            type: 'bar',
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const index = context[0].dataIndex;
                                return chapterTitles[index];
                            },
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };\n'''
    
    for metric_key, title, color in metrics:
        data_values = [stats[metric_key] for stats in all_stats]
        html_content += f'''
        new Chart(document.getElementById('chart_{metric_key}'), {{
            ...chartConfig,
            data: {{
                labels: labels,
                datasets: [{{
                    label: '{title}',
                    data: {data_values},
                    backgroundColor: '{color}',
                    borderColor: '{color}',
                    borderWidth: 1
                }}]
            }}
        }});\n'''
    
    html_content += '''    </script>
</body>
</html>'''
    
    # Write HTML file
    output_path = Path(__file__).parent / 'chapter_analysis.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📊 Charts created: {output_path}")
    print("Opening in browser...\n")
    
    # Open in browser
    import webbrowser
    webbrowser.open(f'file://{output_path.absolute()}')

if __name__ == '__main__':
    chapter_files, totals = main()
    
    # Analyze all chapters again to get individual stats for charts
    all_stats = []
    for filepath in chapter_files:
        stats = analyze_chapter(filepath)
        all_stats.append(stats)
    
    # Create HTML charts
    create_html_charts(chapter_files, all_stats)
