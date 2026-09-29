def square_layout(rows, x, y, w, h):
    total = sum((d['value'] for d in rows))
    vals = [d['value'] * w * h / total for d in rows]
    result = []
    i = 0

    def worst(a, side):
        s = sum(a)
        return max(side * side * max(a) / (s * s), s * s / (side * side * min(a)))
    while i < len(vals):
        row = [vals[i]]
        j = i + 1
        side = min(w, h)
        while j < len(vals) and worst(row + [vals[j]], side) <= worst(row, side):
            row.append(vals[j])
            j += 1
        area = sum(row)
        if w >= h:
            rw = area / h
            yy = y
            for k, a in enumerate(row):
                rh = a / rw
                result.append((rows[i + k], x, yy, rw, rh))
                yy += rh
            x += rw
            w -= rw
        else:
            rh = area / w
            xx = x
            for k, a in enumerate(row):
                rw = a / rh
                result.append((rows[i + k], xx, y, rw, rh))
                xx += rw
            y += rh
            h -= rh
        i = j
    return result

def binary_layout(rows, x, y, w, h):
    if len(rows) == 1:
        return [(rows[0], x, y, w, h)]
    total = sum((d['value'] for d in rows))
    cumulative = 0
    best = None
    for k in range(1, len(rows)):
        cumulative += rows[k - 1]['value']
        delta = abs(cumulative - total / 2)
        if best is None or delta < best[0]:
            best = (delta, k, cumulative)
    _, k, left = best
    if w >= h:
        cut = w * left / total
        return binary_layout(rows[:k], x, y, cut, h) + binary_layout(rows[k:], x + cut, y, w - cut, h)
    cut = h * left / total
    return binary_layout(rows[:k], x, y, w, cut) + binary_layout(rows[k:], x, y + cut, w, h - cut)

def split_layout(rows, x, y, w, h):
    candidates = [square_layout(rows, x, y, w, h), binary_layout(rows, x, y, w, h)]
    return min(candidates, key=lambda rects: max((max(rw / rh, rh / rw) for _, _, _, rw, rh in rects)))
