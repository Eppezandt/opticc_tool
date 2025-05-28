import csv
import pandas as pd

from pprint import pprint

input_file = "insert file path"

na = "n.a."


def csv_to_json(input_file):
    data = {}

    with open(input_file, newline="") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        weights = next(reader)  # skip weights row

        header_count = len(headers) - 1

        for row in reader:
            data[row[0]] = {}

            for i in range(header_count):
                data[row[0]][headers[i + 1]] = row[i + 1]

        return data, headers[1:], weights[1:]


def concodrance_pairwise(data_keys, headers, weights):
    pairwise = {}
    # 1. loop pairwise
    for ic, i in enumerate(sorted_data_keys):
        for jc, j in enumerate(sorted_data_keys):
            for hc, h in enumerate(headers):
                if i == j:
                    pairwise[(i, j, h)] = 0
                else:
                    if (data[i][h] == na) or (data[j][h] == na):
                        pairwise[(i, j, h)] = 0
                    elif float(data[i][h]) >= float(data[j][h]):
                        pairwise[(i, j, h)] = round(float(weights[hc]), 2)
                    else:
                        pairwise[(i, j, h)] = 0
    return pairwise


def discordance_pairwise(data_keys, headers, weights):
    pairwise = {}
    # 1. loop pairwise
    for i in sorted_data_keys:
        for j in sorted_data_keys:
            for h in headers:
                if i == j:
                    pairwise[(i, j, h)] = 0
                else:
                    if (data[i][h] == na) or (data[j][h] == na):
                        pairwise[(i, j, h)] = 0
                    else:
                        pairwise[(i, j, h)] = float(data[j][h]) - float(data[i][h])
    return pairwise


def print_matrix_from_dict(data_dict, sorted_keys, threshold=0.0):
    # Print column headers
    print("      " + " ".join(f"{k:>6}" for k in sorted_keys))
    for ic, i in enumerate(sorted_keys):
        # Print row header
        row = [f"{i:>6}"]
        for jc, j in enumerate(sorted_keys):
            value = data_dict[(i, j)]
            # value = data_dict[(i, j)] if data_dict[(i, j)] >= threshold else 0
            val = f"{value:6.2f}"
            if ic == jc:
                # Invert colors for diagonal (ANSI escape: swap foreground/background)
                val = f"\033[7m{val}\033[0m"
            row.append(val)
        print(" ".join(row))


def get_outranks(pairwise, sorted_data_keys, headers):
    outranks = {}
    for ic, i in enumerate(sorted_data_keys):
        for jc, j in enumerate(sorted_data_keys):
            outranks[(i, j)] = 0
            for hc, h in enumerate(headers):
                pair = (i, j, h)
                # outranks[(i, j)] = round(outranks[(i, j)] + pairwise[pair], 2)
                outranks[(i, j)] = outranks[(i, j)] + pairwise[pair]
            outranks[(i, j)] = round(outranks[(i, j)], 2)
            # print(f"i: {i}, j: {j}, outranks: {outranks[(i, j)]}")
    return outranks


def get_discordance_index(pairwise, sorted_data_keys, headers):
    discordance_index = {}
    for ic, i in enumerate(sorted_data_keys):
        for jc, j in enumerate(sorted_data_keys):
            discordance_index[(i, j)] = 0
            for hc, h in enumerate(headers):
                pair = (i, j, h)
                if discordance_index[(i, j)] < pairwise[pair]:
                    discordance_index[(i, j)] = pairwise[pair]
            discordance_index[(i, j)] = round(discordance_index[(i, j)], 2)
    return discordance_index


def concordance(data, headers, weights, data_keys, sorted_data_keys):
    pairwise = concodrance_pairwise(data_keys, headers, weights)
    # pprint(pairwise)

    # 2. if a > b then use weight, else set weight to 0
    # outranks = {}
    # for ic, i in enumerate(sorted_data_keys):
    #     for jc, j in enumerate(sorted_data_keys):
    #         outranks[(i, j)] = 0
    #         for hc, h in enumerate(headers):
    #             pair = (i, j, h)
    #             # outranks[(i, j)] = round(outranks[(i, j)] + pairwise[pair], 2)
    #             outranks[(i, j)] = outranks[(i, j)] + pairwise[pair]
    #         outranks[(i, j)] = round(outranks[(i, j)], 2)
    #         # print(f"i: {i}, j: {j}, outranks: {outranks[(i, j)]}")
    outranks = get_outranks(pairwise, sorted_data_keys, headers)

    for i in sorted_data_keys:
        for j in sorted_data_keys:
            if i == "A1" and j == "A2":
                for h in headers:
                    # pair = (i, j, h)
                    # print(
                    #     f"i: {i}, j: {j}, h: {h:^5} data: {i} = {data[i][h]:<10} {j} = {data[j][h]:<10} weight: {weights[hc]:<5} outranks: {outranks[(i, j)]} pairwise: {pairwise[(i, j, h)]}"
                    # )
                    pass

    # 3. sum the weight for each row (reduce)

    # 4. set threshold example: 0.51

    threshold = 0.51

    # 5. if sum > threshold then set to keep sum else set to 0

    print_matrix_from_dict(outranks, sorted_data_keys, threshold)

    return outranks, threshold

    # 6. count number dominated

    # dominated = {}
    # for i in sorted_data_keys:
    #     dominated[i] = 0
    #     for j in sorted_data_keys:
    #         # pair = (i, j)
    #         # print(f"i: {i}, j: {j}, data_dict[({i},{j})] {outranks[(i,j)]}")
    #         if outranks[(i, j)] >= threshold:
    #             dominated[i] = dominated[i] + 1

    # 7. print dominated
    # print("Dominated:")
    # for ic, i in enumerate(sorted_data_keys):
    #     print(f"{i:<4s}: {dominated[i]}")

    # 8. print dominated sorted
    # dominated_sorted = sorted(dominated.items(), key=lambda x: x[1], reverse=True)
    # print("\nDominated sorted:")
    # for item in dominated_sorted:
    #     print(f"{item[0]:<4s}: {item[1]}")


def discordance(data, headers, weights, data_keys, sorted_data_keys):
    pairwise = discordance_pairwise(data_keys, headers, weights)
    # pprint(pairwise)

    mins = {}
    maxs = {}
    for hc, h in enumerate(headers):
        for ic, i in enumerate(sorted_data_keys):
            if (data[i][h] == na) or (data[i][h] == ""):
                continue
            value = float(data[i][h])
            if h not in mins:
                mins[h] = value
            if h not in maxs:
                maxs[h] = value
            if value > maxs[h]:
                maxs[h] = value
            if value < mins[h]:
                mins[h] = value

    # print("Min:", mins)
    # print("Max:", maxs)
    ranges = {}
    for hc, h in enumerate(headers):
        if h not in mins:
            ranges[h] = 0
            continue
        ranges[h] = maxs[h] - mins[h]

    # print("Range:", ranges)

    discordance = {}
    for ic, i in enumerate(sorted_data_keys):
        for jc, j in enumerate(sorted_data_keys):
            for hc, h in enumerate(headers):
                if ranges[h] == 0:
                    discordance[(i, j, h)] = 0
                    continue
                discordance[(i, j, h)] = abs(pairwise[(i, j, h)]) / ranges[h]
                # print(
                #     f"i: {i}, j: {j} h: {h}, data[{i}][{j}][{h}]: {pairwise[(i,j,h)]}, mins[h]: {mins[h]}, maxs[h]: {maxs[h]}, ranges[h]: {ranges[h]}"
                # )
    # pprint("Discordance:")
    # pprint(discordance)

    # pprint("Discordance Index:")
    discordance_index = get_discordance_index(discordance, sorted_data_keys, headers)
    # pprint(discordance_index)

    threshold = 0.4

    print_matrix_from_dict(discordance_index, sorted_data_keys, threshold)

    return discordance_index, threshold


def get_domination(
    sorted_data_keys,
    concordance_matrix,
    discordance_matrix,
    concordance_threshold,
    discordance_threshold,
):
    dominates = {}
    dominated = {}
    for i in sorted_data_keys:
        dominates[i] = 0
        dominated[i] = 0

    for i in sorted_data_keys:
        for j in sorted_data_keys:
            if i == j:
                continue
            if (
                concordance_matrix[(i, j)] >= concordance_threshold
                and discordance_matrix[(i, j)] <= discordance_threshold
            ):
                dominates[i] = dominates[i] + 1
                dominated[j] = dominated[j] + 1

            # print(
            #     (
            #         f"i: {i}, j: {j}, "
            #         f"concordance: {concordance_matrix[(i, j)]} "
            #         f"concordance_threshold: {concordance_threshold}"
            #         f"  concordance_dominates: {concordance_matrix[(i, j)] >= concordance_threshold}"
            #         f"  discordance: {discordance_matrix[(i, j)]}"
            #         f"  discordance_threshold: {discordance_threshold}"
            #         f"  discordance_dominates: {discordance_matrix[(i, j)] < discordance_threshold}"
            #     )
            # )
            #
            # if (
            #     concordance_matrix[(i, j)] >= concordance_threshold
            #     and discordance_matrix[(i, j)] <= discordance_threshold
            # ):
            #     dominated[i] = dominated[i] + 1

    netflow = {}
    for ic, i in enumerate(sorted_data_keys):
        netflow[i] = dominates[i] - dominated[i]
        # print(
        #     f"{i:<4s}: Dominates: {dominates[i]} Dominated: {dominated[i]} Netflow: {netflow[i]}"
        # )

    return dominates, dominated, netflow


if __name__ == "__main__":
    data, headers, weights = csv_to_json(input_file)
    data_keys = data.keys()
    sorted_data_keys = sorted(data_keys, key=lambda x: int(x[1:]))

    concordance_matrix, concordance_threshold = concordance(
        data, headers, weights, data_keys, sorted_data_keys
    )
    discordance_matrix, discordance_threshold = discordance(
        data, headers, weights, data_keys, sorted_data_keys
    )

    dominates, dominated, netflow = get_domination(
        sorted_data_keys,
        concordance_matrix,
        discordance_matrix,
        concordance_threshold,
        discordance_threshold,
    )

    # pprint(netflow)
    netflow_sorted = sorted(netflow.items(), key=lambda x: x[1], reverse=True)
    print("Netflow sorted:")
    for rank, item in enumerate(netflow_sorted, 1):
        print(f"{rank}: {item[0]:<4s}: {item[1]}")

    # Export to CSV
    ranking_df = pd.DataFrame(
    [(rank, alt, flow) for rank, (alt, flow) in enumerate(netflow_sorted, 1)],
    columns=["Rank", "Alternative", "Netflow"]
    )
    ranking_df.to_csv("electre_ranking.csv", index=False)
    print("\nELECTRE II ranking saved to 'electre_ranking.csv'")