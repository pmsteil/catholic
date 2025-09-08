#!/usr/bin/env python3
"""
OCIA Table Assignment Script
Based on the Master Prompt (Reusable, 2025+)

Assigns participants to tables based on attendance probability, sex balance,
baptism status, age range, and religious affiliation.
"""

import argparse
import csv
import glob
import hashlib
import os
import sys
from collections import Counter
from typing import Dict, List, Optional


class Participant:
    """Represents a single participant with all their attributes."""
    
    def __init__(self, row_data: Dict[str, str], row_index: int):
        self.row_index = row_index
        self.raw_data = row_data
        
        # Required fields
        self.first_name = row_data.get('First Name', '').strip()
        self.last_name = row_data.get('Last Name', '').strip()
        self.sex = row_data.get('Sex', '').strip()
        self.email = row_data.get('Email Address', '').strip()
        self.phone = row_data.get('Phone', '').strip()
        
        # Parse attendance probability
        self.attendance_raw = row_data.get('Attending Probability', '').strip()
        self.attendance_score = self._parse_attendance()
        
        # Parse age
        self.age_raw = row_data.get('Age', '').strip()
        self.age = self._parse_age()
        self.age_bucket = self._get_age_bucket()
        
        # Parse baptism status
        self.baptized_raw = row_data.get('Have you been baptized?', '').strip()
        self.baptized = self._parse_baptized()
        
        # Other fields
        self.religious_affiliation = row_data.get('Present religious affiliation', '').strip() or 'Unknown'
        self.marital_status = row_data.get('Current Marital Status', '').strip()
        self.baptized_denomination = row_data.get('In what denomination were you baptized?', 
                                                 row_data.get('In what denomination where you baptized?', '')).strip()
        
        # Assignment
        self.table = None
    
    def _parse_attendance(self) -> float:
        """Parse attendance probability to numeric score."""
        if not self.attendance_raw:
            return 0.50  # median fallback
        
        # Handle numeric values (0.7, 1, etc.)
        try:
            val = float(self.attendance_raw)
            if 0 <= val <= 1:
                # Snap to nearest tier
                if val >= 0.85:
                    return 1.00
                elif val >= 0.50:
                    return 0.70
                else:
                    return 0.30
        except ValueError:
            pass
        
        # Handle text values
        text = self.attendance_raw.lower()
        if 'yes' in text:
            return 1.00
        elif 'likely' in text:
            return 0.70
        elif 'not likely' in text:
            return 0.30
        
        return 0.50  # fallback
    
    def _parse_age(self) -> Optional[int]:
        """Parse age to integer."""
        if not self.age_raw:
            return None
        try:
            age = int(float(self.age_raw))
            if 18 <= age <= 120:
                return age
        except ValueError:
            pass
        return None
    
    def _get_age_bucket(self) -> str:
        """Get age bucket for the participant."""
        if self.age is None:
            return 'Unknown'
        
        if 18 <= self.age <= 19:
            return '18-19'
        elif 20 <= self.age <= 25:
            return '20-25'
        elif 26 <= self.age <= 29:
            return '26-29'
        elif 30 <= self.age <= 39:
            return '30-39'
        elif 40 <= self.age <= 49:
            return '40-49'
        else:
            return '50+'
    
    def _parse_baptized(self) -> str:
        """Parse baptism status."""
        if not self.baptized_raw:
            return 'Unknown'
        
        text = self.baptized_raw.lower()
        if 'yes' in text:
            return 'Yes'
        elif 'no' in text:
            return 'No'
        else:
            return 'Unknown'


class TableAssigner:
    """Main class for assigning participants to tables."""
    
    def __init__(self, num_tables: int = 5):
        self.num_tables = num_tables
        self.participants: List[Participant] = []
        self.tables: Dict[int, List[Participant]] = {i: [] for i in range(1, num_tables + 1)}
        self.validation_errors: List[str] = []
        
        # Weights for scoring (baptism status is now highest priority after attendance)
        self.w_baptized = 12  # Much higher priority - second only to attendance
        self.w_sex = 4
        self.w_age = 2
        self.w_affiliation = 1
        self.w_size = 3
        self.w_jitter = 0.001
    
    def select_csv_file(self, filename: Optional[str] = None) -> str:
        """Select CSV file either from command line or interactive selection."""
        if filename:
            if os.path.exists(filename):
                return filename
            else:
                print(f"Error: File '{filename}' not found.")
                sys.exit(1)
        
        # Find CSV files in current directory, excluding _assigned files
        all_csv_files = glob.glob("*.csv")
        csv_files = [f for f in all_csv_files if "_assigned" not in f]
        if not csv_files:
            print("No CSV files found in current directory (excluding _assigned files).")
            sys.exit(1)
        
        print("Available CSV files:")
        for i, file in enumerate(csv_files, 1):
            print(f"{i}. {file}")
        
        while True:
            try:
                choice = input(f"Select file (1-{len(csv_files)}): ").strip()
                index = int(choice) - 1
                if 0 <= index < len(csv_files):
                    return csv_files[index]
                else:
                    print(f"Please enter a number between 1 and {len(csv_files)}")
            except (ValueError, KeyboardInterrupt):
                print("Invalid input. Please enter a number.")
    
    def load_csv(self, filename: str) -> bool:
        """Load and validate CSV file."""
        print(f"Loading CSV file: {filename}")
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
        
        if not rows:
            print("Error: CSV file is empty")
            return False
        
        # Run preflight checks
        if not self._preflight_checks(rows):
            return False
        
        # Load participants
        self.participants = []
        for i, row in enumerate(rows):
            participant = Participant(row, i + 1)
            self.participants.append(participant)
        
        print(f"Loaded {len(self.participants)} participants")
        return True
    
    def _preflight_checks(self, rows: List[Dict[str, str]]) -> bool:
        """Run preflight schema and sanity checks."""
        errors = []
        
        # Required columns
        required_cols = [
            'Attending Probability', 'First Name', 'Last Name', 'Sex', 'Age',
            'Email Address', 'Phone', 'Have you been baptized?',
            'Present religious affiliation', 'Current Marital Status'
        ]
        
        # Check for baptism column variations
        baptism_cols = ['Have you been baptized?', 'Have you been baptized', 'Baptized?', 'Baptized']
        baptism_col_found = any(col in rows[0].keys() for col in baptism_cols)
        
        # Check for denomination column variations  
        denom_cols = ['In what denomination were you baptized?', 'In what denomination where you baptized?']
        denom_col_found = any(col in rows[0].keys() for col in denom_cols)
        
        if not baptism_col_found:
            errors.append("Missing baptism status column")
        if not denom_col_found:
            errors.append("Missing baptism denomination column")
        
        # Check other required columns
        available_cols = set(rows[0].keys())
        for col in required_cols:
            if col not in available_cols and col not in baptism_cols:
                # Check for close synonyms
                found = False
                for available in available_cols:
                    if col.lower().replace(' ', '') in available.lower().replace(' ', ''):
                        found = True
                        break
                if not found:
                    errors.append(f"Missing required column: {col}")
        
        # Sex domain check
        sex_errors = []
        for i, row in enumerate(rows):
            sex = row.get('Sex', '').strip()
            if sex not in ['Male', 'Female']:
                sex_errors.append(f"Row {i+1}: Invalid sex value '{sex}'")
        
        if sex_errors:
            errors.extend(sex_errors[:5])  # Show up to 5 samples
            if len(sex_errors) > 5:
                errors.append(f"... and {len(sex_errors) - 5} more sex validation errors")
        
        # Name validation
        missing_names = 0
        for row in rows:
            first = row.get('First Name', '').strip()
            last = row.get('Last Name', '').strip()
            if not first or not last:
                missing_names += 1
        
        if missing_names > len(rows) * 0.05:  # >5% missing names
            errors.append(f"{missing_names} rows missing first or last name (>{len(rows) * 0.05:.0f} allowed)")
        
        # Contact validation
        missing_contact = 0
        for row in rows:
            email = row.get('Email Address', '').strip()
            phone = row.get('Phone', '').strip()
            if not email and not phone:
                missing_contact += 1
        
        if missing_contact > len(rows) * 0.10:  # >10% missing both
            errors.append(f"{missing_contact} rows missing both email and phone (>{len(rows) * 0.10:.0f} allowed)")
        
        if errors:
            print("\n" + "="*50)
            print("BLOCKING ERRORS — Fix CSV and re-run")
            print("="*50)
            for error in errors:
                print(f"• {error}")
            print("\nNo assignment performed.")
            return False
        
        return True
    
    def print_dataset_summary(self):
        """Print pre-assignment dataset summary."""
        print("\n" + "="*60)
        print("PRE-ASSIGNMENT DATASET SUMMARY")
        print("="*60)
        
        total = len(self.participants)
        print(f"Total participants: {total}")
        
        # Attendance probability
        attendance_counts = Counter(p.attendance_score for p in self.participants)
        print(f"\nAttending Probability:")
        for score in [1.00, 0.70, 0.30]:
            count = attendance_counts.get(score, 0)
            pct = count / total * 100 if total > 0 else 0
            label = {1.00: 'Yes', 0.70: 'Likely', 0.30: 'Not Likely'}[score]
            print(f"  {label} ({score:.2f}): {count} ({pct:.1f}%)")
        
        # Sex
        sex_counts = Counter(p.sex for p in self.participants)
        print(f"\nSex:")
        for sex in ['Male', 'Female']:
            count = sex_counts.get(sex, 0)
            pct = count / total * 100 if total > 0 else 0
            print(f"  {sex}: {count} ({pct:.1f}%)")
        
        # Baptized
        baptized_counts = Counter(p.baptized for p in self.participants)
        print("Validation Results:")
        for status in ['Yes', 'No', 'Unknown']:
            count = baptized_counts.get(status, 0)
            pct = count / total * 100 if total > 0 else 0
            print(f"  {status}: {count} ({pct:.1f}%)")
        
        # Age buckets
        age_counts = Counter(p.age_bucket for p in self.participants)
        print("Table Summary:")
        for bucket in ['18-19', '20-25', '26-29', '30-39', '40-49', '50+', 'Unknown']:
            count = age_counts.get(bucket, 0)
            pct = count / total * 100 if total > 0 else 0
            if count > 0:
                print(f"  {bucket}: {count} ({pct:.1f}%)")
        
        # Religious affiliation
        affiliation_counts = Counter(p.religious_affiliation for p in self.participants)
        print(f"\nPresent religious affiliation:")
        print(f"  Total distinct categories: {len(affiliation_counts)}")
        top_5 = affiliation_counts.most_common(5)
        for affiliation, count in top_5:
            pct = count / total * 100 if total > 0 else 0
            print(f"  {affiliation}: {count} ({pct:.1f}%)")
        
        other_count = sum(count for affiliation, count in affiliation_counts.items() 
                         if affiliation not in [aff for aff, _ in top_5])
        if other_count > 0:
            pct = other_count / total * 100 if total > 0 else 0
            print(f"  Other: {other_count} ({pct:.1f}%)")
    
    def compute_balance_targets(self):
        """Compute global balance targets for all tables."""
        total = len(self.participants)
        target_size = total / self.num_tables
        
        # Table size targets (within ±1)
        base_size = total // self.num_tables
        remainder = total % self.num_tables
        self.table_sizes = [base_size + (1 if i < remainder else 0) for i in range(self.num_tables)]
        
        # Sex targets
        sex_counts = Counter(p.sex for p in self.participants)
        self.sex_targets = {}
        for table_idx in range(self.num_tables):
            table_size = self.table_sizes[table_idx]
            self.sex_targets[table_idx + 1] = {
                'Male': (sex_counts['Male'] / total) * table_size,
                'Female': (sex_counts['Female'] / total) * table_size
            }
        
        # Baptized targets
        baptized_counts = Counter(p.baptized for p in self.participants if p.baptized != 'Unknown')
        baptized_total = sum(baptized_counts.values())
        self.baptized_targets = {}
        for table_idx in range(self.num_tables):
            table_size = self.table_sizes[table_idx]
            if baptized_total > 0:
                self.baptized_targets[table_idx + 1] = {
                    'Yes': (baptized_counts['Yes'] / baptized_total) * table_size,
                    'No': (baptized_counts['No'] / baptized_total) * table_size
                }
            else:
                self.baptized_targets[table_idx + 1] = {'Yes': 0, 'No': 0}
        
        # Age targets
        age_counts = Counter(p.age_bucket for p in self.participants if p.age_bucket != 'Unknown')
        age_total = sum(age_counts.values())
        self.age_targets = {}
        for table_idx in range(self.num_tables):
            table_size = self.table_sizes[table_idx]
            self.age_targets[table_idx + 1] = {}
            if age_total > 0:
                for bucket in ['18-19', '20-25', '26-29', '30-39', '40-49', '50+']:
                    self.age_targets[table_idx + 1][bucket] = (age_counts[bucket] / age_total) * table_size
        
        # Affiliation targets (top 5 + Other)
        affiliation_counts = Counter(p.religious_affiliation for p in self.participants)
        top_5_affiliations = [aff for aff, _ in affiliation_counts.most_common(5)]
        self.affiliation_targets = {}
        for table_idx in range(self.num_tables):
            table_size = self.table_sizes[table_idx]
            self.affiliation_targets[table_idx + 1] = {}
            for affiliation in top_5_affiliations:
                self.affiliation_targets[table_idx + 1][affiliation] = (affiliation_counts[affiliation] / total) * table_size
            
            # Other category
            other_count = sum(count for aff, count in affiliation_counts.items() if aff not in top_5_affiliations)
            self.affiliation_targets[table_idx + 1]['Other'] = (other_count / total) * table_size
    
    def assign_participants(self):
        """Main assignment algorithm using tiered seating with unbaptized priority."""
        self.compute_balance_targets()
        
        # Group participants by attendance tier
        tiers = {1.00: [], 0.70: [], 0.30: []}
        for p in self.participants:
            tiers[p.attendance_score].append(p)
        
        # Assign each tier in order, prioritizing unbaptized distribution
        for tier_score in [1.00, 0.70, 0.30]:
            tier_participants = tiers[tier_score]
            if not tier_participants:
                continue
            
            # Separate baptized and unbaptized in this tier
            unbaptized = [p for p in tier_participants if p.baptized == 'No']
            baptized = [p for p in tier_participants if p.baptized != 'No']
            
            # Compute per-table tier capacities, balancing tier distribution with table capacity
            tier_size = len(tier_participants)
            base_tier_capacity = tier_size // self.num_tables
            tier_remainder = tier_size % self.num_tables
            
            tier_capacities = {}
            for table_num in range(1, self.num_tables + 1):
                # Calculate ideal tier capacity for this table
                ideal_tier_capacity = base_tier_capacity + (1 if (table_num - 1) < tier_remainder else 0)
                
                # Calculate actual remaining table capacity
                current_table_size = len(self.tables[table_num])
                max_table_size = self.table_sizes[table_num - 1]
                remaining_table_capacity = max(0, max_table_size - current_table_size)
                
                # Use the minimum of ideal tier capacity and remaining table capacity
                tier_capacities[table_num] = min(ideal_tier_capacity, remaining_table_capacity)
            
            # First, distribute unbaptized participants evenly
            unbaptized_per_table = len(unbaptized) // self.num_tables
            unbaptized_remainder = len(unbaptized) % self.num_tables
            
            unbaptized_targets = {}
            for table_num in range(1, self.num_tables + 1):
                unbaptized_targets[table_num] = unbaptized_per_table + (1 if (table_num - 1) < unbaptized_remainder else 0)
            
            # Assign unbaptized participants first
            for participant in unbaptized:
                best_table = self._find_best_table_for_unbaptized(participant, tier_capacities, unbaptized_targets)
                self.tables[best_table].append(participant)
                participant.table = best_table
                tier_capacities[best_table] -= 1
                unbaptized_targets[best_table] -= 1
            
            # Then assign baptized participants using regular fairness scoring
            for participant in baptized:
                best_table = self._find_best_table(participant, tier_capacities)
                self.tables[best_table].append(participant)
                participant.table = best_table
                tier_capacities[best_table] -= 1
    
    def _find_best_table(self, participant: Participant, tier_capacities: Dict[int, int]) -> int:
        """Find the best table for a participant using fairness scoring."""
        best_table = None
        best_score = float('inf')
        
        # Only consider tables with remaining tier capacity
        available_tables = [t for t, cap in tier_capacities.items() if cap > 0]
        
        # If no tables have tier capacity, fall back to tables with any remaining capacity
        if not available_tables:
            available_tables = [t for t in range(1, self.num_tables + 1) 
                              if len(self.tables[t]) < self.table_sizes[t - 1]]
        
        # If still no available tables, use the table with the smallest size
        if not available_tables:
            table_sizes = [(len(self.tables[t]), t) for t in range(1, self.num_tables + 1)]
            available_tables = [min(table_sizes)[1]]
        
        for table_num in available_tables:
            score = self._calculate_penalty(participant, table_num)
            
            # Tie-breaking: fewer people, then lowest table number
            current_size = len(self.tables[table_num])
            if score < best_score or (score == best_score and (best_table is None or 
                                                              current_size < len(self.tables[best_table]) or
                                                              (current_size == len(self.tables[best_table]) and table_num < best_table))):
                best_score = score
                best_table = table_num
        
        return best_table
    
    def _find_best_table_for_unbaptized(self, participant: Participant, tier_capacities: Dict[int, int], unbaptized_targets: Dict[int, int]) -> int:
        """Find the best table for an unbaptized participant, prioritizing equal distribution."""
        best_table = None
        best_score = float('inf')
        
        # Only consider tables with remaining tier capacity and unbaptized targets
        available_tables = [t for t, cap in tier_capacities.items() if cap > 0 and unbaptized_targets[t] > 0]
        
        # If no tables have unbaptized targets left, fall back to tables with tier capacity
        if not available_tables:
            available_tables = [t for t, cap in tier_capacities.items() if cap > 0]
        
        # If no tables have tier capacity, fall back to tables with any remaining capacity
        if not available_tables:
            available_tables = [t for t in range(1, self.num_tables + 1) 
                              if len(self.tables[t]) < self.table_sizes[t - 1]]
        
        # If still no available tables, use the table with the smallest size
        if not available_tables:
            table_sizes = [(len(self.tables[t]), t) for t in range(1, self.num_tables + 1)]
            available_tables = [min(table_sizes)[1]]
        
        for table_num in available_tables:
            # Heavy preference for tables that still need unbaptized participants
            if unbaptized_targets[table_num] > 0:
                score = 0  # Highest priority
            else:
                score = 1000  # Lower priority if unbaptized quota already met
            
            # Add secondary considerations (sex, age, etc.) but with much lower weights
            score += self._calculate_penalty(participant, table_num) * 0.1
            
            # Tie-breaking: fewer people, then lowest table number
            current_size = len(self.tables[table_num])
            if score < best_score or (score == best_score and (best_table is None or 
                                                              current_size < len(self.tables[best_table]) or
                                                              (current_size == len(self.tables[best_table]) and table_num < best_table))):
                best_score = score
                best_table = table_num
        
        return best_table
    
    def _calculate_penalty(self, participant: Participant, table_num: int) -> float:
        """Calculate penalty score for assigning participant to table."""
        penalty = 0.0
        current_table = self.tables[table_num]
        
        # Sex balance penalty
        current_sex_counts = Counter(p.sex for p in current_table)
        new_sex_counts = current_sex_counts.copy()
        new_sex_counts[participant.sex] += 1
        
        sex_penalty = 0
        for sex in ['Male', 'Female']:
            target = self.sex_targets[table_num][sex]
            actual = new_sex_counts[sex]
            sex_penalty += abs(actual - target)
        penalty += self.w_sex * sex_penalty
        
        # Baptized balance penalty
        if participant.baptized != 'Unknown':
            current_baptized_counts = Counter(p.baptized for p in current_table if p.baptized != 'Unknown')
            new_baptized_counts = current_baptized_counts.copy()
            new_baptized_counts[participant.baptized] += 1
            
            baptized_penalty = 0
            for status in ['Yes', 'No']:
                target = self.baptized_targets[table_num][status]
                actual = new_baptized_counts[status]
                baptized_penalty += abs(actual - target)
            penalty += self.w_baptized * baptized_penalty
        
        # Age balance penalty
        if participant.age_bucket != 'Unknown':
            current_age_counts = Counter(p.age_bucket for p in current_table if p.age_bucket != 'Unknown')
            new_age_counts = current_age_counts.copy()
            new_age_counts[participant.age_bucket] += 1
            
            age_penalty = 0
            for bucket in ['18-19', '20-25', '26-29', '30-39', '40-49', '50+']:
                target = self.age_targets[table_num].get(bucket, 0)
                actual = new_age_counts[bucket]
                age_penalty += abs(actual - target)
            penalty += self.w_age * age_penalty
        
        # Affiliation balance penalty
        current_affiliation_counts = Counter()
        top_5_affiliations = list(self.affiliation_targets[table_num].keys())
        top_5_affiliations.remove('Other')  # Handle separately
        
        for p in current_table:
            if p.religious_affiliation in top_5_affiliations:
                current_affiliation_counts[p.religious_affiliation] += 1
            else:
                current_affiliation_counts['Other'] += 1
        
        new_affiliation_counts = current_affiliation_counts.copy()
        if participant.religious_affiliation in top_5_affiliations:
            new_affiliation_counts[participant.religious_affiliation] += 1
        else:
            new_affiliation_counts['Other'] += 1
        
        affiliation_penalty = 0
        for affiliation in self.affiliation_targets[table_num]:
            target = self.affiliation_targets[table_num][affiliation]
            actual = new_affiliation_counts[affiliation]
            affiliation_penalty += abs(actual - target)
        penalty += self.w_affiliation * affiliation_penalty
        
        # Table size pressure penalty - prevent exceeding target size
        current_size = len(current_table)
        target_size = self.table_sizes[table_num - 1]
        # Extremely high penalty if this would exceed the target size
        if (current_size + 1) > target_size:
            penalty += 10000  # Blocking penalty to prevent exceeding target
        else:
            # Small penalty for being at target size to prefer smaller tables when equal
            if current_size == target_size:
                penalty += 1
        
        # Deterministic tie-break using hash
        hash_input = f"{participant.email}{table_num}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest()[:8], 16) / (16**8)
        penalty += self.w_jitter * hash_value
        
        return penalty
    
    def generate_output_csv(self, input_filename: str):
        """Generate assignment CSV with Table column first, sorted by table then attendance."""
        output_filename = input_filename.replace('.csv', '_assigned.csv')
        
        with open(input_filename, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_fieldnames = reader.fieldnames
            # Put Table first, then all other columns
            fieldnames = ['Table'] + original_fieldnames
            
            # Sort participants by table number, then by attendance probability (descending)
            sorted_participants = sorted(self.participants, 
                                       key=lambda p: (p.table, -p.attendance_score))
            
            with open(output_filename, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for participant in sorted_participants:
                    row = {'Table': participant.table}
                    row.update(participant.raw_data)
                    writer.writerow(row)
        
        print(f"Assignment CSV saved as: {output_filename}")
        return output_filename
    
    def print_table_summary(self):
        """Print table summary report."""
        print("\n" + "="*60)
        print("TABLE SUMMARY REPORT")
        print("="*60)
        
        for table_num in range(1, self.num_tables + 1):
            table_participants = self.tables[table_num]
            print(f"\nTable {table_num} ({len(table_participants)} participants):")
            
            # Sex breakdown
            sex_counts = Counter(p.sex for p in table_participants)
            male_count = sex_counts.get('Male', 0)
            female_count = sex_counts.get('Female', 0)
            total = len(table_participants)
            male_pct = (male_count / total * 100) if total > 0 else 0
            female_pct = (female_count / total * 100) if total > 0 else 0
            print(f"  Sex: {male_count}M ({male_pct:.1f}%) / {female_count}F ({female_pct:.1f}%)")
            
            # Baptized breakdown
            baptized_counts = Counter(p.baptized for p in table_participants)
            for status in ['Yes', 'No', 'Unknown']:
                count = baptized_counts.get(status, 0)
                pct = (count / total * 100) if total > 0 else 0
                if count > 0:
                    print(f"  Baptized {status}: {count} ({pct:.1f}%)")
            
            # Attendance tier breakdown
            attendance_counts = Counter(p.attendance_score for p in table_participants)
            print("Attendance:", end="")
            for score in [1.00, 0.70, 0.30]:
                count = attendance_counts.get(score, 0)
                if count > 0:
                    label = {1.00: 'Yes', 0.70: 'Likely', 0.30: 'Not Likely'}[score]
                    print(f" {label}:{count}", end="")
            print()
            
            # Age breakdown
            age_counts = Counter(p.age_bucket for p in table_participants)
            age_parts = []
            for bucket in ['18-19', '20-25', '26-29', '30-39', '40-49', '50+', 'Unknown']:
                count = age_counts.get(bucket, 0)
                if count > 0:
                    age_parts.append(f"{bucket}:{count}")
            if age_parts:
                print(f"  Ages: {' '.join(age_parts)}")
            
            # Top affiliations
            affiliation_counts = Counter(p.religious_affiliation for p in table_participants)
            top_affiliations = affiliation_counts.most_common(3)
            if top_affiliations:
                affiliation_parts = [f"{aff}:{count}" for aff, count in top_affiliations]
                print(f"  Affiliations: {' '.join(affiliation_parts)}")
        
        # Global diagnostics
        print(f"\nGlobal Diagnostics:")
        table_sizes = [len(self.tables[i]) for i in range(1, self.num_tables + 1)]
        print(f"  Table sizes: {'/'.join(map(str, table_sizes))}")
        
        # Sex deviation
        sex_deviations = []
        for table_num in range(1, self.num_tables + 1):
            table_participants = self.tables[table_num]
            sex_counts = Counter(p.sex for p in table_participants)
            total = len(table_participants)
            if total > 0:
                male_pct = (sex_counts.get('Male', 0) / total) * 100
                female_pct = (sex_counts.get('Female', 0) / total) * 100
                sex_deviations.extend([male_pct, female_pct])
        
        if sex_deviations:
            max_sex_dev = max(sex_deviations) - min(sex_deviations)
            print(f"  Max sex deviation: {max_sex_dev:.1f} percentage points")
        
        # Baptized deviation
        baptized_deviations = []
        for table_num in range(1, self.num_tables + 1):
            table_participants = self.tables[table_num]
            baptized_counts = Counter(p.baptized for p in table_participants if p.baptized != 'Unknown')
            total = sum(baptized_counts.values())
            if total > 0:
                yes_pct = (baptized_counts.get('Yes', 0) / total) * 100
                no_pct = (baptized_counts.get('No', 0) / total) * 100
                baptized_deviations.extend([yes_pct, no_pct])
        
        if baptized_deviations:
            max_baptized_dev = max(baptized_deviations) - min(baptized_deviations)
            print(f"  Max baptized deviation: {max_baptized_dev:.1f} percentage points")
        
        # Attendance tier spread
        print("  Attendance tier spread:")
        for score in [1.00, 0.70, 0.30]:
            tier_counts = []
            for table_num in range(1, self.num_tables + 1):
                count = sum(1 for p in self.tables[table_num] if p.attendance_score == score)
                tier_counts.append(count)
            label = {1.00: 'Yes', 0.70: 'Likely', 0.30: 'Not Likely'}[score]
            print(f"    {label}: {'/'.join(map(str, tier_counts))}")
    
    def validate_assignment(self) -> bool:
        """Run validation and reconciliation checks."""
        print("\n" + "="*60)
        print("VALIDATION CHECKLIST")
        print("="*60)
        
        all_passed = True
        
        # Count reconciliation
        total_assigned = sum(len(self.tables[i]) for i in range(1, self.num_tables + 1))
        total_participants = len(self.participants)
        if total_assigned == total_participants:
            print("✓ PASS: Count reconciliation")
        else:
            print(f"✗ FAIL: Count reconciliation ({total_assigned} assigned vs {total_participants} participants)")
            all_passed = False
        
        # Size band check
        table_sizes = [len(self.tables[i]) for i in range(1, self.num_tables + 1)]
        min_size, max_size = min(table_sizes), max(table_sizes)
        if max_size - min_size <= 1:
            print(f"✓ PASS: Size band (sizes: {'/'.join(map(str, table_sizes))})")
        else:
            print(f"✗ FAIL: Size band (sizes: {'/'.join(map(str, table_sizes))}, deviation: {max_size - min_size})")
            all_passed = False
        
        # Sex totals
        assigned_sex_counts = Counter()
        for table_num in range(1, self.num_tables + 1):
            for p in self.tables[table_num]:
                assigned_sex_counts[p.sex] += 1
        
        original_sex_counts = Counter(p.sex for p in self.participants)
        sex_match = all(assigned_sex_counts[sex] == original_sex_counts[sex] for sex in ['Male', 'Female'])
        if sex_match:
            print("✓ PASS: Sex totals")
        else:
            print("✗ FAIL: Sex totals")
            all_passed = False
        
        # Baptized totals
        assigned_baptized_counts = Counter()
        for table_num in range(1, self.num_tables + 1):
            for p in self.tables[table_num]:
                assigned_baptized_counts[p.baptized] += 1
        
        original_baptized_counts = Counter(p.baptized for p in self.participants)
        baptized_match = all(assigned_baptized_counts[status] == original_baptized_counts[status] 
                           for status in ['Yes', 'No', 'Unknown'])
        if baptized_match:
            print("✓ PASS: Baptized totals")
        else:
            print("✗ FAIL: Baptized totals")
            all_passed = False
        
        # Attendance tiers
        tier_validation_passed = True
        for score in [1.00, 0.70, 0.30]:
            tier_participants = [p for p in self.participants if p.attendance_score == score]
            tier_size = len(tier_participants)
            if tier_size == 0:
                continue
            
            # Check tier distribution across tables
            assigned_tier_counts = []
            for table_num in range(1, self.num_tables + 1):
                count = sum(1 for p in self.tables[table_num] if p.attendance_score == score)
                assigned_tier_counts.append(count)
            
            expected_base = tier_size // self.num_tables
            expected_remainder = tier_size % self.num_tables
            expected_counts = [expected_base + (1 if i < expected_remainder else 0) 
                             for i in range(self.num_tables)]
            
            if assigned_tier_counts == expected_counts:
                label = {1.00: 'Yes', 0.70: 'Likely', 0.30: 'Not Likely'}[score]
                print(f"✓ PASS: Attendance tier {label}")
            else:
                label = {1.00: 'Yes', 0.70: 'Likely', 0.30: 'Not Likely'}[score]
                print(f"✗ FAIL: Attendance tier {label}")
                tier_validation_passed = False
        
        if tier_validation_passed:
            print("✓ PASS: All attendance tiers")
        else:
            all_passed = False
        
        # Age totals
        assigned_age_counts = Counter()
        for table_num in range(1, self.num_tables + 1):
            for p in self.tables[table_num]:
                assigned_age_counts[p.age_bucket] += 1
        
        original_age_counts = Counter(p.age_bucket for p in self.participants)
        age_match = all(assigned_age_counts[bucket] == original_age_counts[bucket] 
                       for bucket in original_age_counts.keys())
        if age_match:
            print("✓ PASS: Age totals")
        else:
            print("✗ FAIL: Age totals")
            all_passed = False
        
        # Unassigned participants
        unassigned = [p for p in self.participants if p.table is None]
        if len(unassigned) == 0:
            print("✓ PASS: Unassigned participants (0)")
        else:
            print(f"✗ FAIL: Unassigned participants ({len(unassigned)})")
            all_passed = False
        
        if not all_passed:
            print("\n⚠️  MANUAL REVIEW NEEDED - Some validation checks failed")
        else:
            print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        
        return all_passed


def main():
    """Main function to run the table assignment process."""
    parser = argparse.ArgumentParser(description='OCIA Table Assignment Script')
    parser.add_argument('-f', '--file', help='Input CSV filename')
    parser.add_argument('-t', '--tables', type=int, help='Number of tables (default: 5)')
    
    args = parser.parse_args()
    
    # Get number of tables
    num_tables = args.tables
    if num_tables is None:
        while True:
            try:
                num_tables = int(input("Enter number of tables (default 5): ") or "5")
                if num_tables > 0:
                    break
                else:
                    print("Number of tables must be positive")
            except ValueError:
                print("Please enter a valid number")
    
    print(f"Using {num_tables} tables")
    
    # Create assigner
    assigner = TableAssigner(num_tables)
    
    # Select and load CSV file
    filename = assigner.select_csv_file(args.file)
    if not assigner.load_csv(filename):
        sys.exit(1)
    
    print("Dataset Summary:")
    assigner.print_dataset_summary()
    
    # Run assignment algorithm
    print("\n" + "="*60)
    print("RUNNING ASSIGNMENT ALGORITHM")
    print("="*60)
    print("Assigning participants to tables...")
    
    assigner.assign_participants()
    
    # Generate outputs
    assigner.generate_output_csv(filename)
    assigner.print_table_summary()
    assigner.validate_assignment()


if __name__ == "__main__":
    main()