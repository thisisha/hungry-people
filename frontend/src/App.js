import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import {
  Search as SearchIcon,
  Restaurant as RestaurantIcon,
  Event as EventIcon,
  LocationOn as LocationIcon
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [regions, setRegions] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    loadRegions();
    loadInitialData();
  }, []);

  const loadRegions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/regions`);
      if (response.data.success) {
        setRegions(response.data.data);
      }
    } catch (err) {
      console.error('지역 목록 로드 실패:', err);
    }
  };

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [restaurantsRes, eventsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/restaurants?limit=20`),
        axios.get(`${API_BASE_URL}/events?limit=20`)
      ]);

      if (restaurantsRes.data.success) {
        setRestaurants(restaurantsRes.data.data);
      }
      if (eventsRes.data.success) {
        setEvents(eventsRes.data.data);
      }
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_BASE_URL}/search`, {
        params: { q: searchQuery, limit: 20 }
      });

      if (response.data.success) {
        setRestaurants(response.data.data.restaurants);
        setEvents(response.data.data.events);
      }
    } catch (err) {
      setError('검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegionFilter = async (region) => {
    setSelectedRegion(region);
    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_BASE_URL}/restaurants`, {
        params: { region: region, limit: 20 }
      });

      if (response.data.success) {
        setRestaurants(response.data.data);
      }
    } catch (err) {
      setError('지역별 필터링 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleRecommendation = async (location) => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_BASE_URL}/recommendations`, {
        params: { location: location, limit: 10 }
      });

      if (response.data.success) {
        setRestaurants(response.data.data);
        setActiveTab(0); // 백년가게 탭으로 이동
      }
    } catch (err) {
      setError('추천 서비스 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const RestaurantCard = ({ restaurant }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" alignItems="center" mb={1}>
          <RestaurantIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h3">
            {restaurant.name}
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          <LocationIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
          {restaurant.address}
        </Typography>
        {restaurant.phone && (
          <Typography variant="body2" color="text.secondary">
            📞 {restaurant.phone}
          </Typography>
        )}
        <Chip 
          label={restaurant.region} 
          size="small" 
          color="primary" 
          sx={{ mt: 1 }}
        />
      </CardContent>
    </Card>
  );

  const EventCard = ({ event }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" alignItems="center" mb={1}>
          <EventIcon color="secondary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h3">
            {event.event_name}
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          <LocationIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
          {event.location}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          📅 {event.start_date} {event.end_date !== event.start_date && `~ ${event.end_date}`}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          🏢 {event.host_organization}
        </Typography>
        <Box mt={1}>
          <Chip 
            label={event.region} 
            size="small" 
            color="secondary" 
            sx={{ mr: 1 }}
          />
          {event.tech_category && (
            <Chip 
              label={event.tech_category} 
              size="small" 
              variant="outlined"
            />
          )}
        </Box>
        <CardActions sx={{ p: 0, mt: 1 }}>
          <Button 
            size="small" 
            onClick={() => handleRecommendation(event.location)}
          >
            근처 백년가게 추천
          </Button>
        </CardActions>
      </CardContent>
    </Card>
  );

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <RestaurantIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Hungry People - 식사 장소 추천 서비스
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* 검색 및 필터 섹션 */}
        <Box mb={4}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="검색어 입력"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <Button onClick={handleSearch}>
                      <SearchIcon />
                    </Button>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>지역 선택</InputLabel>
                <Select
                  value={selectedRegion}
                  onChange={(e) => handleRegionFilter(e.target.value)}
                  label="지역 선택"
                >
                  <MenuItem value="">전체 지역</MenuItem>
                  {regions.map((region) => (
                    <MenuItem key={region} value={region}>
                      {region}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>

        {/* 에러 메시지 */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* 로딩 인디케이터 */}
        {loading && (
          <Box display="flex" justifyContent="center" mb={2}>
            <CircularProgress />
          </Box>
        )}

        {/* 탭 네비게이션 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label={`백년가게 (${restaurants.length})`} />
            <Tab label={`행사일정 (${events.length})`} />
          </Tabs>
        </Box>

        {/* 백년가게 탭 */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            {restaurants.map((restaurant) => (
              <Grid item xs={12} sm={6} md={4} key={restaurant.id}>
                <RestaurantCard restaurant={restaurant} />
              </Grid>
            ))}
            {restaurants.length === 0 && !loading && (
              <Grid item xs={12}>
                <Typography variant="h6" color="text.secondary" align="center">
                  백년가게 정보가 없습니다.
                </Typography>
              </Grid>
            )}
          </Grid>
        )}

        {/* 행사일정 탭 */}
        {activeTab === 1 && (
          <Grid container spacing={3}>
            {events.map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.id}>
                <EventCard event={event} />
              </Grid>
            ))}
            {events.length === 0 && !loading && (
              <Grid item xs={12}>
                <Typography variant="h6" color="text.secondary" align="center">
                  행사일정 정보가 없습니다.
                </Typography>
              </Grid>
            )}
          </Grid>
        )}
      </Container>
    </div>
  );
}

export default App;
