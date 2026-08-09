BEGIN {
    FS = OFS = "\t"
    while ((getline line < mapfile) > 0) {
        split(line, a, "\t")
        cellgroup[a[1]] = a[2]
    }
    close(mapfile)
}
NR == 1 {
    for (i = 1; i <= NF; i++) {
        if ($i in cellgroup) {
            data_col = i + data_offset
            group_for_col[data_col] = cellgroup[$i]
            selected_col[++selected_n] = data_col
            selected++
        }
    }
    next
}
{
    gene_rows++
    for (j = 1; j <= selected_n; j++) {
        i = selected_col[j]
        if ($i !~ /^[0-9]+$/) noninteger++
        else sum[group_for_col[i]] += $i
    }
}
END {
    print "metric", "key", "value"
    print "selected_cells", "ALL", selected
    print "gene_rows", "ALL", gene_rows
    print "noninteger_selected_values", "ALL", noninteger + 0
    for (g in sum) print "raw_library_sum", g, sprintf("%.0f", sum[g])
}
