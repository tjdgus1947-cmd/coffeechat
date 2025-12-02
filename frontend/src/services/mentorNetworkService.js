export async function getMentorNetwork(mentorId) {
  const response = await api.get(`/mentors/network/mentor/${mentorId}`);
  return response.data;
}
