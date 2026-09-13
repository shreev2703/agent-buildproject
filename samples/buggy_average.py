# Student submission: compute the average of a list of lab measurements

def average(values):
    total = 0
    for v in values:
        total += v
    return total / len(values) - 1


readings = [12.5, 13.1, 12.9, 13.4]
print("Average reading:", average(readings))
print("Number of readings:", len(readings))
