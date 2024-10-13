import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, Image, TouchableOpacity, Linking } from 'react-native';
import axios from 'axios';

const RecommendationsScreen = ({ route }) => {
  const [recommendations, setRecommendations] = useState([]);
  const { eventId } = route.params;

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/recommendations/${eventId}`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const renderRecommendationItem = ({ item }) => (
    <View style={styles.recommendationItem}>
      <Image source={{ uri: item.image_url }} style={styles.giftImage} />
      <View style={styles.giftInfo}>
        <Text style={styles.giftTitle}>{item.title}</Text>
        <Text style={styles.giftPrice}>{item.price} {item.currency_code}</Text>
        <TouchableOpacity
          style={styles.viewButton}
          onPress={() => Linking.openURL(item.url)}
        >
          <Text style={styles.viewButtonText}>View on {item.source}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Gift Recommendations</Text>
      <FlatList
        data={recommendations}
        renderItem={renderRecommendationItem}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#121212',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#ffffff',
  },
  recommendationItem: {
    flexDirection: 'row',
    backgroundColor: '#1e1e1e',
    padding: 15,
    borderRadius: 5,
    marginBottom: 10,
  },
  giftImage: {
    width: 80,
    height: 80,
    borderRadius: 5,
  },
  giftInfo: {
    flex: 1,
    marginLeft: 15,
  },
  giftTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  giftPrice: {
    fontSize: 14,
    color: '#b3b3b3',
    marginTop: 5,
  },
  viewButton: {
    backgroundColor: '#0dcaf0',
    padding: 8,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 10,
  },
  viewButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default RecommendationsScreen;
