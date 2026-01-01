// Mock data for development/testing when backend is unavailable

export const MOCK_LOGIN_RESPONSE = {
    token: 'mock-token-12345',
    user: {
        id: 1,
        username: 'jsmith',
        email: 'john.smith@eastsidevolleyball.com',
        first_name: 'John',
        last_name: 'Smith',
    },
    profile: {
        id: 1,
        user: 1,
        jersey_number: 7,
        position: 'Outside Hitter',
        height: '6\'1"',
        year: 'Junior',
    },
};

export const MOCK_PLAYER_PROFILE = {
    id: 1,
    user: 1,
    jersey_number: 7,
    position: 'Outside Hitter',
    height: '6\'1"',
    year: 'Junior',
    hometown: 'Seattle, WA',
    club_team: 'Eastside Volleyball Club',
    high_school: 'Lincoln High School',
};

export const MOCK_PLAYER_STATS = {
    id: 1,
    player: 1,
    season: 2024,
    kills: 312,
    blocks: 28,
    aces: 45,
    digs: 198,
    kill_attempts: 742,
    attack_efficiency: 0.376,
    pass_rating: 2.2,
    matches_played: 24,
};

export const MOCK_AI_SUMMARY = {
    id: 1,
    player: 1,
    summary: 'John is an exceptional outside hitter with outstanding offensive production. His kill efficiency of 37.6% is top-tier for the position. Focus areas: Improve first-pass consistency to increase setter options.',
    generated_at: '2024-12-24T10:00:00Z',
};

export const MOCK_ANNOUNCEMENTS = [
    {
        id: 1,
        title: 'Regional Tournament This Weekend',
        message: 'Don\'t forget - we have the regional tournament starting Friday at 3 PM. All players must arrive 2 hours early for warm-ups and team meeting.',
        created_by: 'Coach Sarah',
        created_at: '2024-12-23T08:00:00Z',
        is_urgent: true,
    },
    {
        id: 2,
        title: 'New Practice Schedule Posted',
        message: 'The updated practice schedule for January has been posted. Check the team calendar for details. We\'ll be training harder to prepare for the state championship.',
        created_by: 'Coach Sarah',
        created_at: '2024-12-22T14:30:00Z',
        is_urgent: false,
    },
    {
        id: 3,
        title: 'Congratulations Team!',
        message: 'Amazing performance at yesterday\'s match! We showed great teamwork and communication. Final score: Eastside 25-18 vs Northside.',
        created_by: 'Coach Sarah',
        created_at: '2024-12-20T18:00:00Z',
        is_urgent: false,
    },
];

export const MOCK_VIDEOS = [
    {
        id: 1,
        title: 'Eastside vs Lincoln - Full Match',
        description: 'Full match recording: Eastside Volleyball defeats Lincoln High School 25-17, 25-19',
        video_url: 'https://example.com/videos/eastside-vs-lincoln.mp4',
        thumbnail_url: 'https://via.placeholder.com/400x300?text=Eastside+vs+Lincoln',
        uploaded_at: '2024-12-20T19:00:00Z',
        duration: '45:30',
    },
    {
        id: 2,
        title: 'Highlights: Eastside vs Riverside',
        description: 'Game highlights: Amazing plays and incredible teamwork in this 3-set victory',
        video_url: 'https://example.com/videos/eastside-vs-riverside-highlights.mp4',
        thumbnail_url: 'https://via.placeholder.com/400x300?text=Eastside+vs+Riverside',
        uploaded_at: '2024-12-18T20:00:00Z',
        duration: '8:45',
    },
    {
        id: 3,
        title: 'Training Session - Serving Techniques',
        description: 'Coach Sarah demonstrates advanced serving techniques. Learn the mechanics of jump serves and float serves.',
        video_url: 'https://example.com/videos/serving-techniques.mp4',
        thumbnail_url: 'https://via.placeholder.com/400x300?text=Serving+Techniques',
        uploaded_at: '2024-12-16T15:00:00Z',
        duration: '12:20',
    },
    {
        id: 4,
        title: 'Eastside vs Central Park - Full Match',
        description: 'Full match recording: Regional championship semi-final. Eastside advances 25-23, 24-26, 25-20',
        video_url: 'https://example.com/videos/eastside-vs-central.mp4',
        thumbnail_url: 'https://via.placeholder.com/400x300?text=Eastside+vs+Central',
        uploaded_at: '2024-12-15T18:30:00Z',
        duration: '52:15',
    },
];
