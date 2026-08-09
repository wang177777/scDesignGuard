#define _GNU_SOURCE
#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { char *cell; char *group; } Entry;

static int cmp_entry(const void *a, const void *b) {
    return strcmp(((const Entry *)a)->cell, ((const Entry *)b)->cell);
}

static Entry *find_entry(Entry *entries, size_t n, const char *cell) {
    Entry key = {(char *)cell, NULL};
    return bsearch(&key, entries, n, sizeof(Entry), cmp_entry);
}

static int group_id(char ***groups, size_t *ng, const char *name) {
    for (size_t i = 0; i < *ng; ++i) if (strcmp((*groups)[i], name) == 0) return (int)i;
    *groups = realloc(*groups, (*ng + 1) * sizeof(char *));
    if (!*groups) { perror("realloc"); exit(2); }
    (*groups)[*ng] = strdup(name);
    return (int)(*ng)++;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s MAPFILE DATA_OFFSET < decompressed_matrix\n", argv[0]);
        return 2;
    }
    int data_offset = atoi(argv[2]);
    FILE *mf = fopen(argv[1], "r");
    if (!mf) { perror("mapfile"); return 2; }
    Entry *entries = NULL; size_t n = 0, cap = 0;
    char *line = NULL; size_t linecap = 0; ssize_t len;
    while ((len = getline(&line, &linecap, mf)) >= 0) {
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        char *tab = strchr(line, '\t'); if (!tab) continue; *tab = 0;
        if (n == cap) { cap = cap ? cap * 2 : 1024; entries = realloc(entries, cap * sizeof(Entry)); }
        entries[n].cell = strdup(line); entries[n].group = strdup(tab + 1); n++;
    }
    fclose(mf); free(line); line = NULL; linecap = 0;
    qsort(entries, n, sizeof(Entry), cmp_entry);

    len = getline(&line, &linecap, stdin);
    if (len < 0) { fprintf(stderr, "empty matrix\n"); return 2; }
    while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
    size_t header_n = 1;
    for (char *p = line; *p; ++p) if (*p == '\t') header_n++;
    size_t cols = header_n + (data_offset > 0 ? (size_t)data_offset : 0);
    int *group_for_col = malloc(cols * sizeof(int));
    for (size_t i = 0; i < cols; ++i) group_for_col[i] = -1;
    char **groups = NULL; size_t ng = 0, col = 0, selected = 0;
    char *save = NULL;
    for (char *tok = strtok_r(line, "\t", &save); tok; tok = strtok_r(NULL, "\t", &save), ++col) {
        Entry *e = find_entry(entries, n, tok);
        if (e) {
            size_t data_col = col + (size_t)data_offset;
            group_for_col[data_col] = group_id(&groups, &ng, e->group);
            selected++;
        }
    }
    unsigned long long *sums = calloc(ng, sizeof(unsigned long long));
    unsigned long long gene_rows = 0, noninteger = 0;
    while ((len = getline(&line, &linecap, stdin)) >= 0) {
        while (len && (line[len-1] == '\n' || line[len-1] == '\r')) line[--len] = 0;
        gene_rows++; col = 0; save = NULL;
        for (char *tok = strtok_r(line, "\t", &save); tok; tok = strtok_r(NULL, "\t", &save), ++col) {
            if (col >= cols || group_for_col[col] < 0) continue;
            char *p = tok; if (!*p) { noninteger++; continue; }
            while (*p && isdigit((unsigned char)*p)) p++;
            if (*p) { noninteger++; continue; }
            errno = 0; unsigned long long v = strtoull(tok, NULL, 10);
            if (errno) { noninteger++; continue; }
            sums[group_for_col[col]] += v;
        }
    }
    printf("metric\tkey\tvalue\n");
    printf("selected_cells\tALL\t%zu\n", selected);
    printf("gene_rows\tALL\t%llu\n", gene_rows);
    printf("noninteger_selected_values\tALL\t%llu\n", noninteger);
    for (size_t i = 0; i < ng; ++i) printf("raw_library_sum\t%s\t%llu\n", groups[i], sums[i]);
    return 0;
}
