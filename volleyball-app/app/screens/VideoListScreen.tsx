import { Ionicons } from '@expo/vector-icons';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, FlatList, Image, RefreshControl, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { apiClient } from '../api/client';

interface Video {
  id: number;
  title: string;
  description: string;
  game_type: string;
  game_date: string | null;
  opponent: string;
  thumbnail: string | null;
  duration_seconds: number;
  view_count: number;
  uploaded_by_name: string;
  uploaded_at: string;
}

export default function VideoListScreen() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setError(null);
      const data = await apiClient.getGameVideos();
      setVideos(data.data || []);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setError('Failed to load videos');
      Alert.alert('Error', 'Failed to load videos');
      console.error('Videos loading error:', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      setError(null);
      const data = await apiClient.getGameVideos();
      setVideos(data.data || []);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setError('Failed to refresh videos');
      console.error('Videos refresh error:', errorMsg);
    } finally {
      setRefreshing(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const renderVideoCard = ({ item }: { item: Video }) => (
    <TouchableOpacity style={styles.videoCard} activeOpacity={0.7}>
      <View style={styles.thumbnailContainer}>
        {item.thumbnail ? (
          <Image source={{ uri: item.thumbnail }} style={styles.thumbnail} />
        ) : (
          <View style={[styles.thumbnail, styles.thumbnailPlaceholder]}>
            <Ionicons name="play-circle" size={48} color="#fff" />
          </View>
        )}
        <View style={styles.durationBadge}>
          <Text style={styles.durationText}>{formatDuration(item.duration_seconds)}</Text>
        </View>
      </View>

      <View style={styles.videoInfo}>
        <Text style={styles.videoTitle} numberOfLines={2}>{item.title}</Text>

        <View style={styles.metadataRow}>
          <View style={styles.typeTag}>
            <Text style={styles.typeTagText}>{item.game_type.toUpperCase()}</Text>
          </View>
          <Text style={styles.uploadedBy}>{item.uploaded_by_name}</Text>
        </View>

        {item.opponent && (
          <Text style={styles.opponent}>vs {item.opponent}</Text>
        )}

        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Ionicons name="eye" size={16} color="#666" />
            <Text style={styles.statText}>{item.view_count} views</Text>
          </View>
          <Text style={styles.uploadDate}>{formatDate(item.uploaded_at)}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (error && videos.length === 0) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="alert-circle" size={48} color="#FF3B30" />
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.retryText}>Pull down to retry</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={videos}
      renderItem={renderVideoCard}
      keyExtractor={(item) => item.id.toString()}
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      ListEmptyComponent={
        <View style={styles.emptyContainer}>
          <Ionicons name="videocam-off" size={48} color="#ccc" />
          <Text style={styles.emptyText}>No videos available</Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 12,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    marginTop: 12,
    textAlign: 'center',
  },
  retryText: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginTop: 12,
  },
  videoCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  thumbnailContainer: {
    position: 'relative',
    width: '100%',
    height: 200,
  },
  thumbnail: {
    width: '100%',
    height: '100%',
    backgroundColor: '#e0e0e0',
  },
  thumbnailPlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#333',
  },
  durationBadge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  durationText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  videoInfo: {
    padding: 12,
  },
  videoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
  },
  metadataRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  typeTag: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginRight: 8,
  },
  typeTagText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  uploadedBy: {
    fontSize: 12,
    color: '#666',
  },
  opponent: {
    fontSize: 12,
    color: '#999',
    marginBottom: 8,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  uploadDate: {
    fontSize: 12,
    color: '#999',
  },
});
