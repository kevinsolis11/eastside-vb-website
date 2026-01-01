import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { apiClient } from '../api/client';

interface Profile {
  user: {
    first_name: string;
    last_name: string;
    email: string;
  };
  player: {
    number: number;
    position: string;
  } | null;
  position: string;
  height: string;
}

export default function PlayerProfileScreen() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getPlayerProfile();
      setProfile(data);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      Alert.alert('Error', 'Failed to load profile');
      console.error('Profile loading error:', errorMsg);
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

  if (!profile) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Profile not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Personal Information</Text>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Name:</Text>
          <Text style={styles.value}>
            {profile.user.first_name} {profile.user.last_name}
          </Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.label}>Email:</Text>
          <Text style={styles.value}>{profile.user.email}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Volleyball Information</Text>
        {profile.player && (
          <>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Number:</Text>
              <Text style={styles.value}>#{profile.player.number}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Position:</Text>
              <Text style={styles.value}>{profile.player.position || 'Not set'}</Text>
            </View>
          </>
        )}
        {profile.position && (
          <View style={styles.infoRow}>
            <Text style={styles.label}>Secondary Position:</Text>
            <Text style={styles.value}>{profile.position}</Text>
          </View>
        )}
        {profile.height && (
          <View style={styles.infoRow}>
            <Text style={styles.label}>Height:</Text>
            <Text style={styles.value}>{profile.height}</Text>
          </View>
        )}
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
  infoRow: {
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
    color: '#000',
    fontWeight: '500',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 20,
  },
});
