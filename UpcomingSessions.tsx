import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Avatar, AvatarFallback } from "../ui/avatar";
import { 
  Calendar, 
  Clock, 
  Video, 
  MapPin,
  MoreVertical
} from "lucide-react";
import { ImageWithFallback } from "../figma/ImageWithFallback";

const sessions = [
  {
    id: 1,
    mentee: "김민지",
    avatar: "https://images.unsplash.com/photo-1610387694365-19fafcc86d86?w=100",
    topic: "프로덕트 전략 상담",
    date: "오늘",
    time: "14:00 - 15:00",
    type: "online",
    status: "confirmed",
  },
  {
    id: 2,
    mentee: "이준호",
    avatar: "https://images.unsplash.com/photo-1719400471588-575b23e27bd7?w=100",
    topic: "커리어 전환 조언",
    date: "내일",
    time: "10:00 - 11:00",
    type: "offline",
    location: "강남역 스타벅스",
    status: "confirmed",
  },
  {
    id: 3,
    mentee: "박서연",
    avatar: "https://images.unsplash.com/photo-1738750908048-14200459c3c9?w=100",
    topic: "스타트업 창업 멘토링",
    date: "11월 8일",
    time: "16:00 - 17:00",
    type: "online",
    status: "pending",
  },
];

export function UpcomingSessions() {
  return (
    <Card className="p-6 border-0 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="mb-1">다가오는 세션</h3>
          <p className="text-gray-600 text-sm">예정된 멘토링 일정</p>
        </div>
        <Button variant="outline" size="sm">
          전체보기
        </Button>
      </div>

      <div className="space-y-4">
        {sessions.map((session) => (
          <div
            key={session.id}
            className="p-4 rounded-lg border hover:border-blue-300 hover:bg-blue-50/50 transition-all"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <ImageWithFallback
                  src={session.avatar}
                  alt={session.mentee}
                  className="w-12 h-12 rounded-full object-cover"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <span>{session.mentee}</span>
                    <Badge
                      variant={session.status === "confirmed" ? "default" : "secondary"}
                      className={session.status === "confirmed" 
                        ? "bg-green-100 text-green-700 hover:bg-green-200" 
                        : "bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
                      }
                    >
                      {session.status === "confirmed" ? "확정" : "대기중"}
                    </Badge>
                  </div>
                  <p className="text-gray-600 text-sm">{session.topic}</p>
                </div>
              </div>
              <button className="text-gray-400 hover:text-gray-600">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-600 ml-15">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{session.date}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{session.time}</span>
              </div>
              {session.type === "online" ? (
                <div className="flex items-center gap-1 text-blue-600">
                  <Video className="w-4 h-4" />
                  <span>온라인</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-purple-600">
                  <MapPin className="w-4 h-4" />
                  <span>{session.location}</span>
                </div>
              )}
            </div>

            {session.status === "pending" && (
              <div className="flex gap-2 mt-3 pt-3 border-t">
                <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-700">
                  승인
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  거절
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
