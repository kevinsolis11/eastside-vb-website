import { Ionicons } from '@expo/vector-icons';
import React, { useContext, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { apiClient } from '../api/client';
import { AuthContext } from '../context/AuthContext';

interface DashboardScreenProps {
  navigation: any;
}

export default function PlayerDashboardScreen({ navigation }: DashboardScreenProps) {
  const [playerProfile, setPlayerProfile] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileRes, statsRes] = await Promise.all([
        apiClient.getPlayerProfile(),
        apiClient.getPlayerStats(),
      ]);
      setPlayerProfile(profileRes.data);
      setStats(statsRes.data);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      console.error('Error loading dashboard:', errorMsg);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Your Profile</Text>
        </View>
        <View style={styles.cardBody}>
          {playerProfile ? (
            <>
              <View style={styles.profileRow}>
                <Text style={styles.label}>Player Name</Text>
                <Text style={styles.value}>
                  {playerProfile.player?.first_name} {playerProfile.player?.last_name}
                </Text>
              </View>
              {playerProfile.player?.number && (
                <View style={styles.profileRow}>
                  <Text style={styles.label}>Number</Text>
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>#{playerProfile.player.number}</Text>
                  </View>
                </View>
              )}
              {playerProfile.player?.position && (
                <View style={styles.profileRow}>
                  <Text style={styles.label}>Position</Text>
                  <Text style={styles.value}>{playerProfile.player.position}</Text>
                </View>
              )}
              {playerProfile.height && (
                <View style={styles.profileRow}>
                  <Text style={styles.label}>Height</Text>
                  <Text style={styles.value}>{playerProfile.height}</Text>
                </View>
              )}
              <TouchableOpacity
                style={styles.button}
                onPress={() => navigation.navigate('PlayerProfile')}>
                <Ionicons name="pencil" size={16} color="#fff" />
                <Text style={styles.buttonText}>View Profile</Text>
              </TouchableOpacity>
            </>
          ) : (
            <Text style={styles.emptyText}>No profile data available</Text>
          )}
        </View>
      </View>

      {stats && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Your Statistics</Text>
          </View>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Ionicons name="flash" size={24} color="#007AFF" />
              <Text style={styles.statLabel}>Kills</Text>
              <Text style={styles.statValue}>{stats.kills || 0}</Text>
            </View>
            <View style={styles.statItem}>
              <Ionicons name="shield" size={24} color="#17C0EB" />
              <Text style={styles.statLabel}>Blocks</Text>
              <Text style={styles.statValue}>{stats.blocks || 0}</Text>
            </View>
            <View style={styles.statItem}>
              <Ionicons name="star" size={24} color="#34C759" />
              <Text style={styles.statLabel}>Aces</Text>
              <Text style={styles.statValue}>{stats.aces || 0}</Text>
            </View>
            <View style={styles.statItem}>
              <Ionicons name="hand-left" size={24} color="#FF9500" />
              <Text style={styles.statLabel}>Digs</Text>
              <Text style={styles.statValue}>{stats.digs || 0}</Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('PlayerStats')}>
            <Ionicons name="bar-chart" size={16} color="#fff" />
            <Text style={styles.buttonText}>Detailed Stats</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.linksContainer}>
        <TouchableOpacity style={styles.linkButton}>
          <Ionicons name="megaphone" size={24} color="#FF6B6B" />
          <Text style={styles.linkText}>Announcements</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.linkButton}>
          <Ionicons name="play-circle" size={24} color="#4ECDC4" />
          <Text style={styles.linkText}>Team Videos</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    backgroundColor: '#007AFF',
    padding: 16,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  cardBody: {
    padding: 16,
  },
  profileRow: {
    marginBottom: 12,
  },
  label: {
    fontSize: 12,
    color: '#999',
    fontWeight: '500',
    marginBottom: 4,
  },
  value: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  badge: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  badgeText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  button: {
    backgroundColor: '#007AFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    gap: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
  emptyText: {
    color: '#999',
    textAlign: 'center',
    paddingVertical: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  statItem: {
    width: '50%',
    alignItems: 'center',
    paddingVertical: 12,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  statValue: {
    fontSize: 22,
    fontWeight: '700',
    color: '#333',
    marginTop: 2,
  },
  linksContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  linkButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  linkText: {
    fontSize: 12,
    color: '#333',
    marginTop: 8,
    textAlign: 'center',
    fontWeight: '500',
  },
});
