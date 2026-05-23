.pragma library

function columnWidth(column, defaultColumnWidth) {
    if (column && column.width !== undefined) {
        return column.width;
    }
    return defaultColumnWidth;
}

function stretchCount(columns) {
    var count = 0;
    for (var i = 0; i < columns.length; i += 1) {
        if (columns[i] && columns[i].stretch) {
            count += 1;
        }
    }
    // return count > 0 ? count : columns.length;
    return count
}

function columnCanStretch(columns, column) {
    if (!column) {
        return false;
    }

    // var explicitStretchCount = 0;
    // for (var i = 0; i < columns.length; i += 1) {
    //     if (columns[i] && columns[i].stretch) {
    //         explicitStretchCount += 1;
    //     }
    // }
    // return explicitStretchCount > 0 ? column.stretch : true;
    return column.stretch
}

function baseTotalWidth(columns, defaultColumnWidth) {
    var total = 0;
    for (var i = 0; i < columns.length; i += 1) {
        total += columnWidth(columns[i], defaultColumnWidth);
    }
    return total;
}

function availableWidth(rootWidth, columns, defaultColumnWidth) {
    return Math.max(rootWidth, baseTotalWidth(columns, defaultColumnWidth));
}

function totalWidth(rootWidth, columns, defaultColumnWidth) {
    var total = 0;
    var stretchable = stretchCount(columns);
    var baseTotal = baseTotalWidth(columns, defaultColumnWidth);
    var extra = Math.max(0, availableWidth(rootWidth, columns, defaultColumnWidth) - baseTotal);
    for (var i = 0; i < columns.length; i += 1) {
        var column = columns[i];
        var width = columnWidth(column, defaultColumnWidth);
        if (columnCanStretch(columns, column) && stretchable > 0) {
            width += extra / stretchable;
        }
        total += width;
    }
    return Math.max(total, rootWidth);
}

function resolvedColumnWidth(rootWidth, columns, defaultColumnWidth, column) {
    var width = columnWidth(column, defaultColumnWidth);
    if (!columnCanStretch(columns, column)) {
        return width;
    }

    var stretchable = stretchCount(columns);
    if (stretchable <= 0) {
        return width;
    }

    var extra = Math.max(
        0,
        availableWidth(rootWidth, columns, defaultColumnWidth) - baseTotalWidth(columns, defaultColumnWidth)
    );
    return width + extra / stretchable;
}
