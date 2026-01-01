import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { apiClient } from '../api/client';

interface Stats {
  id: number;
  kills: number;
  blocks: number;
  aces: number;
  digs: number;
  updated_at: string | null;
}

export default function PlayerStatsScreen() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getPlayerStats();
      setStats(data);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      Alert.alert('Error', 'Failed to load stats');
      console.error('Stats loading error:', errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!stats) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>No stats available</Text>
      </View>
    );
  }

  const statItems = [
    { label: 'Kills', value: stats.kills, icon: '⚡' },
    { label: 'Blocks', value: stats.blocks, icon: '🛡️' },
    { label: 'Aces', value: stats.aces, icon: '��' },
    { label: 'Digs', value: stats.digs, icon: '🏐' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.statsGrid}>
        {statItems.map((item, index) => (
          <View key={index} style={styles.statCard}>
            <Text style={styles.statIcon}>{item.icon}</Text>
            <Text style={styles.statValue}>{item.value}</Text>
            <Text style={styles.statLabel}>{item.label}</Text>
          </View>
        ))}
      </View>

      {stats.updated_at && (
        <View style={styles.updateInfo}>
          <Text style={styles.updateText}>
            Last updated: {new Date(stats.updated_at).toLocaleDateString()}
          </Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Season Overview</Text>
        <View style={styles.statRow}>
          <Text style={styles.label}>Total Points:</Text>
          <Text style={styles.value}>{stats.kills + stats.aces}</Text>
        </View>
        <View style={styles.statRow}>
          <Text style={styles.label}>Defensive Stats:</Text>
          <Text style={styles.value}>{stats.blocks + stats.digs}</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    width: '48%',
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  updateInfo: {
    alignItems: 'center',
    marginBottom: 20,
  },
  updateText: {
    fontSize: 12,
    color: '#999',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
    color: '#000',
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666',
  },
  value: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
  },
});
