import pandas as pd
import matplotlib.pyplot as plt
import re
from create_album_jsons import *
import random
import numpy as np


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


def compute_ranking_losses_extended(df):
    loss_y_vs_t, loss_y_vs_s, loss_t_vs_s = [], [], []

    for _, row in df.iterrows():

        y_list, t_list, s_list = row['Yagiz'], row['Tugba'], get_top_5_popular_tracks(row['spotify_id'], sp)

        def get_rank_dict(rank_list):
            return {idx: rank for rank, idx in enumerate(rank_list, start=1)}

        def compute_loss(a_list, b_list):
            a_ranks, b_ranks = get_rank_dict(a_list), get_rank_dict(b_list)
            union = set(a_list) | set(b_list)
            a_missing = [idx for idx in b_list if idx not in a_ranks]
            b_missing = [idx for idx in a_list if idx not in b_ranks]

            for i, idx in enumerate(a_missing, 6): a_ranks[idx] = i
            for i, idx in enumerate(b_missing, 6): b_ranks[idx] = i

            return sum(abs(a_ranks[i] - b_ranks[i]) for i in union)

        loss_y_vs_t.append(compute_loss(y_list, t_list))
        loss_y_vs_s.append(compute_loss(y_list, s_list))
        loss_t_vs_s.append(compute_loss(t_list, s_list))

    df = df.copy()
    df['loss_y_vs_t'] = loss_y_vs_t
    df['loss_y_vs_s'] = loss_y_vs_s
    df['loss_t_vs_s'] = loss_t_vs_s
    return df


def extend_df_with_spotify(df):
    """
    Adds 'Spotify' and 'total_songs' columns to the given DataFrame:
    - 'Spotify' contains the top-5 most popular track indices.
    - 'total_songs' is the number of tracks on the album.
    """
    spotify_rankings = []
    total_song_counts = []

    for _, row in df.iterrows():
        album_id = row['spotify_id']
        album = sp.album(album_id)

        # Get popular track indices (as before)
        spotify_top5 = get_top_5_popular_tracks(album_id, sp)
        spotify_rankings.append(spotify_top5)

        # Count the number of songs
        total_song_counts.append(len(album['tracks']['items']))

    df = df.copy()
    df['Spotify'] = spotify_rankings
    df['total_songs'] = total_song_counts
    return df


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


def plot_all_ranking_similarities(df):
    albums = df['album'].tolist()
    plt.figure(figsize=(12, 6))

    plt.plot(albums, df['similarity_y_vs_t'], marker='o', label='Yagiz vs Tugba')
    plt.plot(albums, df['similarity_y_vs_s'], marker='s', label='Yagiz vs Spotify')
    plt.plot(albums, df['similarity_t_vs_s'], marker='^', label='Tugba vs Spotify')

    plt.title('Ranking Similarities')
    plt.ylabel('Similarity')
    plt.xticks(rotation=90)
    plt.xlabel('Album')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def make_slug(album_name):
    slug = album_name.lower()                     # Lowercase
    slug = slug.replace(' ', '-')                 # Replace spaces with hyphens
    slug = re.sub(r'[^\w\-]', '', slug)           # Remove anything that's not a word char or hyphen
    return slug


def simulate_ranking_loss(k, top_n=5, num_trials=100000, seed=42):
    """
    Monte Carlo estimation of expected ranking loss for albums with k songs.

    Args:
        k (int): Total number of songs in the album.
        top_n (int): Number of top songs selected by each user (typically 5).
        num_trials (int): Number of random trials for the simulation.
        seed (int): Random seed for reproducibility.

    Returns:
        (mean_loss, std_loss): Tuple of expected value and standard deviation of the loss.
    """
    rng = random.Random(seed)
    all_losses = []

    song_ids = list(range(k))  # use simple integer song IDs

    for _ in range(num_trials):
        y_list = rng.sample(song_ids, top_n)
        t_list = rng.sample(song_ids, top_n)

        y_ranks = {idx: rank for rank, idx in enumerate(y_list, start=1)}
        t_ranks = {idx: rank for rank, idx in enumerate(t_list, start=1)}

        union_songs = list(set(y_list) | set(t_list))

        missing_in_y = [idx for idx in t_list if idx not in y_ranks]
        missing_in_t = [idx for idx in y_list if idx not in t_ranks]

        next_rank_y = top_n + 1
        for idx in missing_in_y:
            y_ranks[idx] = next_rank_y
            next_rank_y += 1

        next_rank_t = top_n + 1
        for idx in missing_in_t:
            t_ranks[idx] = next_rank_t
            next_rank_t += 1

        loss = sum(abs(y_ranks[idx] - t_ranks[idx]) for idx in union_songs)
        all_losses.append(loss)

    return np.mean(all_losses), np.std(all_losses)


def compute_similarity_score(loss, baseline_stats, k):
    """
    Compute the music taste similarity score (flipped Z-score).
    """
    stats = baseline_stats.get(str(k))
    if not stats:
        return None  # fallback if no baseline for this k
    mean = stats['mean']
    std = stats['std']
    if std == 0:
        return 0  # avoid division by zero
    z = (loss - mean) / std
    return -z  # flip: higher is better (more similarity)
