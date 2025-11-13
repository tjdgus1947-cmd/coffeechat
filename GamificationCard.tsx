import { Card } from "../ui/card";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { 
  Trophy, 
  Target, 
  Zap, 
  Award,
  Crown,
  Star
} from "lucide-react";

const badges = [
  { icon: Trophy, name: "신규 멘토", color: "bg-blue-100 text-blue-600", earned: true },
  { icon: Star, name: "평점 마스터", color: "bg-yellow-100 text-yellow-600", earned: true },
  { icon: Zap, name: "빠른 응답", color: "bg-purple-100 text-purple-600", earned: true },
  { icon: Award, name: "베테랑", color: "bg-green-100 text-green-600", earned: false },
  { icon: Crown, name: "전문가", color: "bg-orange-100 text-orange-600", earned: false },
];

export function GamificationCard() {
  const currentLevel = 7;
  const currentXP = 3420;
  const nextLevelXP = 5000;
  const progress = (currentXP / nextLevelXP) * 100;
  const totalPoints = 12450;

  return (
    <Card className="p-6 border-0 shadow-lg bg-gradient-to-br from-blue-600 to-purple-600 text-white">
      <div className="space-y-6">
        {/* Level & Points */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <Trophy className="w-6 h-6" />
              </div>
              <div>
                <p className="text-white/80 text-sm">현재 레벨</p>
                <div className="text-3xl">Level {currentLevel}</div>
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-white/80 text-sm">총 포인트</p>
            <div className="text-2xl">{totalPoints.toLocaleString()}P</div>
          </div>
        </div>

        {/* Progress to Next Level */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>다음 레벨까지</span>
            <span>{currentXP.toLocaleString()} / {nextLevelXP.toLocaleString()} XP</span>
          </div>
          <Progress value={progress} className="h-3 bg-white/20" />
        </div>

        {/* Badges */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-white">획득한 배지</h4>
            <span className="text-sm text-white/80">3/5</span>
          </div>
          <div className="flex gap-3">
            {badges.map((badge, index) => (
              <div
                key={index}
                className={`relative ${
                  badge.earned ? "opacity-100" : "opacity-40"
                }`}
                title={badge.name}
              >
                <div className={`w-12 h-12 rounded-xl ${
                  badge.earned 
                    ? "bg-white/90" 
                    : "bg-white/20"
                } flex items-center justify-center`}>
                  <badge.icon className={`w-6 h-6 ${
                    badge.earned 
                      ? badge.color.split(' ')[1]
                      : "text-white/60"
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Info */}
        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/20">
          <div className="text-center">
            <p className="text-white/80 text-sm mb-1">이번 주</p>
            <div>+340 XP</div>
          </div>
          <div className="text-center">
            <p className="text-white/80 text-sm mb-1">랭킹</p>
            <div>#12</div>
          </div>
          <div className="text-center">
            <p className="text-white/80 text-sm mb-1">목표</p>
            <div>80%</div>
          </div>
        </div>
      </div>
    </Card>
  );
}
