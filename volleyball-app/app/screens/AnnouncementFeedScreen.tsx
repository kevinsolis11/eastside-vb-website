import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { apiClient } from '../api/client';

export default function AnnouncementFeedScreen() {
  const [announcements, setAnnouncements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnnouncements();
  }, []);

  const loadAnnouncements = async () => {
    try {
      setError(null);
      const response = await apiClient.getAnnouncements();
      setAnnouncements(response.data || []);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error loading announcements:', errorMsg);
      setError('Failed to load announcements');
      Alert.alert('Error', 'Failed to load announcements');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      setError(null);
      const response = await apiClient.getAnnouncements();
      setAnnouncements(response.data || []);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error refreshing announcements:', errorMsg);
      setError('Failed to refresh announcements');
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (error && announcements.length === 0) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.retryText}>Pull down to refresh</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={announcements}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={[styles.announcementCard, item.is_urgent && styles.urgent]}>
            {item.is_urgent && (
              <Text style={styles.urgentBadge}>URGENT</Text>
            )}
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.message}>{item.message}</Text>
            <Text style={styles.date}>
              {new Date(item.created_at).toLocaleDateString()}
            </Text>
          </View>
        )}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No announcements yet</Text>
          </View>
        }
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  retryText: {
    color: '#666',
    fontSize: 14,
    marginTop: 8,
  },
  announcementCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  urgent: {
    borderLeftColor: '#FF3B30',
    backgroundColor: '#fff5f5',
  },
  urgentBadge: {
    color: '#FF3B30',
    fontWeight: '700',
    fontSize: 12,
    marginBottom: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  message: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  date: {
    fontSize: 12,
    color: '#999',
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyText: {
    color: '#999',
    fontSize: 16,
  },
});
