# NCV Level 4 Advanced Python - Community Water Consumption and Billing
# Name: __________________ Student number: __________________ Date: __________
# Reads municipal water readings, validates records, calculates progressive bills,
# ranks the top five consumers manually, and writes reports.
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUT = BASE / 'water_readings.txt'
REPORT = BASE / 'billing_report.txt'
ERRORS = BASE / 'errors.log'

# SECTION 1: BILLING AND CLASSIFICATION
def calculate_bill(usage):
    if usage <= 6:
        return 0.0
    elif usage <= 20:
        return (usage - 6) * 8.50
    else:
        return 14 * 8.50 + (usage - 20) * 12.00

def classify(usage):
    if usage <= 20:
        return 'LOW'
    elif usage <= 50:
        return 'MODERATE'
    else:
        return 'HIGH'

# SECTION 2: READ AND VALIDATE
def read_records(path):
    records = {}
    errors = []
    total = 0
    try:
        with open(path, 'r', encoding='utf-8-sig') as file:
            for line_number, raw_line in enumerate(file, start=1):
                total += 1
                line = raw_line.strip()
                parts = [part.strip() for part in line.split(',')]
                reasons = []
                if len(parts) != 5:
                    reasons.append('expected exactly 5 comma-separated fields')
                elif not line or any(part == '' for part in parts):
                    reasons.append('missing required field')
                else:
                    meter, name, previous_text, current_text, area = parts
                    if meter in records:
                        reasons.append('duplicate meter number')
                    try:
                        previous = float(previous_text)
                        current = float(current_text)
                        if not (previous == previous and current == current and abs(previous) != float('inf') and abs(current) != float('inf')):
                            reasons.append('non-finite reading')
                        elif previous < 0 or current < 0:
                            reasons.append('negative reading')
                        elif current < previous:
                            reasons.append('current reading below previous reading')
                    except ValueError:
                        reasons.append('non-numeric reading')
                    if not reasons:
                        usage = current - previous
                        records[meter] = {
                            'name': name, 'previous': previous, 'current': current,
                            'area': area, 'usage': usage,
                            'bill': calculate_bill(usage), 'category': classify(usage)
                        }
                if reasons:
                    errors.append(f'Line {line_number}: {line!r} | REJECTED: {"; ".join(reasons)}')
    except FileNotFoundError:
        errors.append(f'INPUT FILE MISSING: {path.name}. Place it in the same folder as water_billing.py.')
    except OSError as exc:
        errors.append(f'INPUT FILE ERROR: {exc}')
    return records, errors, total

# SECTION 3: MANUAL TOP FIVE RANKING (NO sorted/max/min)
def top_five(records):
    ranked = []
    for meter in records:
        ranked.append((records[meter]['usage'], meter))
    for i in range(len(ranked) - 1):
        for j in range(len(ranked) - 1 - i):
            if ranked[j][0] < ranked[j + 1][0]:
                ranked[j], ranked[j + 1] = ranked[j + 1], ranked[j]
    return ranked[:5]

# SECTION 4: WRITE REPORTS
def write_reports(records, errors, total):
    accepted = len(records)
    rejected = total - accepted
    total_usage = 0
    total_billed = 0
    counts = {'LOW': 0, 'MODERATE': 0, 'HIGH': 0}
    lines = ['COMMUNITY WATER CONSUMPTION AND BILLING REPORT', '=' * 95,
             f'{"Meter":<9} {"Household":<22} {"Area":<18} {"Previous":>9} {"Current":>9} {"Usage kL":>9} {"Category":<9} {"Bill R":>10}', '-' * 110]
    for meter, record in records.items():
        total_usage += record['usage']
        total_billed += record['bill']
        counts[record['category']] += 1
        lines.append(f'{meter:<9} {record["name"][:22]:<22} {record["area"][:18]:<18} {record["previous"]:>9.2f} {record["current"]:>9.2f} {record["usage"]:>9.2f} {record["category"]:<9} {record["bill"]:>10.2f}')
    lines += ['', 'TOP FIVE WATER CONSUMERS', '-' * 55]
    for rank, (usage, meter) in enumerate(top_five(records), start=1):
        lines.append(f'{rank}. {meter} | {records[meter]["name"]} | {usage:.2f} kL')
    lines += ['', 'SUMMARY', '-' * 55,
              f'Input lines processed: {total}', f'Accepted records: {accepted}',
              f'Rejected records: {rejected}', f'Total consumption: {total_usage:.2f} kL',
              f'Total billed: R{total_billed:.2f}',
              f'LOW households: {counts["LOW"]}',
              f'MODERATE households: {counts["MODERATE"]}',
              f'HIGH households: {counts["HIGH"]}']
    with open(REPORT, 'w', encoding='utf-8') as file:
        file.write('\n'.join(lines) + '\n')
    with open(ERRORS, 'w', encoding='utf-8') as file:
        file.write('\n'.join(errors) + ('\n' if errors else 'No rejected records.\n'))
    return accepted, rejected, total_usage, total_billed

# SECTION 5: TESTS
def run_tests():
    cases = [(0, 0.0), (6, 0.0), (7, 8.50), (20, 119.0), (25, 179.0), (50, 479.0), (51, 491.0)]
    print('TARIFF TESTS:')
    for usage, expected in cases:
        actual = calculate_bill(usage)
        print(f'{usage} kL | Expected R{expected:.2f} | Actual R{actual:.2f} | {"PASS" if abs(actual-expected)<0.00001 else "FAIL"}')
    assert classify(20) == 'LOW'
    assert classify(50) == 'MODERATE'
    assert classify(51) == 'HIGH'
    sample = {'A': {'usage': 10}, 'B': {'usage': 30}, 'C': {'usage': 20}, 'D': {'usage': 40}, 'E': {'usage': 50}, 'F': {'usage': 60}}
    assert [meter for _, meter in top_five(sample)] == ['F', 'E', 'D', 'B', 'C']
    print('Classification and manual ranking tests: PASS')

def main():
    print('NCV LEVEL 4 - WATER BILLING MANAGEMENT SYSTEM')
    run_tests()
    records, errors, total = read_records(INPUT)
    accepted, rejected, usage, billed = write_reports(records, errors, total)
    print(f'Input lines: {total} | Accepted: {accepted} | Rejected: {rejected}')
    print(f'Total consumption: {usage:.2f} kL | Total billed: R{billed:.2f}')
    print(f'Reports saved: {REPORT.name}, {ERRORS.name}')
    if not INPUT.exists():
        print('WARNING: water_readings.txt was not found. Supply the official 220-record dataset and run again.')

if __name__ == '__main__':
    main()
