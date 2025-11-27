import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { Trophy, Medal, Award, TrendingUp } from "lucide-react";
import { ImageWithFallback } from "../figma/ImageWithFallback";

const topMentors = [
  {
    rank: 1,
    name: "김태희",
    avatar: "https://images.unsplash.com/photo-1610387694365-19fafcc86d86?w=100",
    points: 15420,
    category: "프로덕트",
    badge: "Gold",
  },
  {
    rank: 2,
    name: "이준호",
    avatar: "https://images.unsplash.com/photo-1719400471588-575b23e27bd7?w=100",
    points: 14850,
    category: "개발",
    badge: "Gold",
  },
  {
    rank: 3,
    name: "박서연",
    avatar: "https://images.unsplash.com/photo-1738750908048-14200459c3c9?w=100",
    points: 13990,
    category: "마케팅",
    badge: "Silver",
  },
];

export function MentorRanking() {
  const myRank = 12;
  const myPoints = 12450;

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Award className="w-5 h-5 text-orange-500" />;
    return null;
  };

  return (
    <Card className="p-6 border-0 shadow-lg">
      <div className="mb-6">
        <h3 className="mb-1">멘토 랭킹</h3>
        <p className="text-gray-600 text-sm">이번 달 상위 멘토</p>
      </div>

      {/* My Rank */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white flex items-center justify-center">
              #{myRank}
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-0.5">내 순위</p>
              <div className="flex items-center gap-2">
                <span>나</span>
                <TrendingUp className="w-4 h-4 text-green-600" />
                <span className="text-green-600 text-sm">+3</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600 mb-0.5">포인트</p>
            <span className="text-blue-600">{myPoints.toLocaleString()}P</span>
          </div>
        </div>
      </div>

      {/* Top 3 */}
      <div className="space-y-3">
        {topMentors.map((mentor) => (
          <div
            key={mentor.rank}
            className={`flex items-center justify-between p-3 rounded-lg ${
              mentor.rank === 1 
                ? 'bg-yellow-50 border border-yellow-200' 
                : mentor.rank === 2
                ? 'bg-gray-50 border border-gray-200'
                : 'bg-orange-50 border border-orange-200'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8">
                {getRankIcon(mentor.rank)}
              </div>
              <ImageWithFallback
                src={mentor.avatar}
                alt={mentor.name}
                className="w-10 h-10 rounded-full object-cover"
              />
              <div>
                <div className="flex items-center gap-2">
                  <span>{mentor.name}</span>
                  <Badge 
                    variant="secondary" 
                    className={
                      mentor.badge === "Gold" 
                        ? "bg-yellow-100 text-yellow-700" 
                        : "bg-gray-100 text-gray-700"
                    }
                  >
                    {mentor.badge}
                  </Badge>
                </div>
                <p className="text-xs text-gray-600">{mentor.category}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm">{mentor.points.toLocaleString()}P</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t text-center">
        <p className="text-sm text-gray-600">
          상위 10위 진입까지 <span className="text-blue-600">1,200P</span> 필요
        </p>
      </div>
    </Card>
  );
}
