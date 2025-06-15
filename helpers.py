import pandas as pd
import matplotlib.pyplot as plt


def compute_ranking_loss_df(df):
    """
    Returns a new DataFrame with an additional 'loss' column.
    Loss is total sum of absolute rank differences over union of both top-5 lists.
    Missing songs are assigned increasing virtual ranks (6, 7, ...) on the missing side.
    """
    loss_list = []

    for _, row in df.iterrows():
        y_list = row['Yagiz']
        t_list = row['Tugba']

        # Build actual rank dictionaries
        y_ranks = {idx: rank for rank, idx in enumerate(y_list, start=1)}
        t_ranks = {idx: rank for rank, idx in enumerate(t_list, start=1)}

        # Union of all selected songs
        union_songs = list(set(y_list) | set(t_list))

        # Assign virtual ranks for missing songs
        missing_in_y = [idx for idx in t_list if idx not in y_ranks]
        missing_in_t = [idx for idx in y_list if idx not in t_ranks]

        next_rank_y = 6
        for idx in missing_in_y:
            y_ranks[idx] = next_rank_y
            next_rank_y += 1

        next_rank_t = 6
        for idx in missing_in_t:
            t_ranks[idx] = next_rank_t
            next_rank_t += 1

        # Now compute absolute rank differences
        total_loss = sum(abs(y_ranks[idx] - t_ranks[idx]) for idx in union_songs)
        loss_list.append(total_loss)

    df_with_loss = df.copy()
    df_with_loss['loss'] = loss_list
    return df_with_loss


def plot_ranking_losses(ranking_loss_df):
    losses = ranking_loss_df['loss'].tolist()
    album_names = ranking_loss_df['album'].tolist()

    plt.figure(figsize=(10, 5))
    plt.plot(album_names, losses, marker='o', label='Loss', linewidth = 2)
    plt.title('Disagreement Loss per Album')
    plt.xlabel('Album Name')
    plt.ylabel('Loss')
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

