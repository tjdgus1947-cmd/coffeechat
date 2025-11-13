import { Card } from "../ui/card";
import { Star } from "lucide-react";
import { ImageWithFallback } from "../figma/ImageWithFallback";

const reviews = [
  {
    id: 1,
    mentee: "김민지",
    avatar: "https://images.unsplash.com/photo-1610387694365-19fafcc86d86?w=100",
    rating: 5,
    comment: "정말 유익한 시간이었습니다. 구체적이고 실질적인 조언 감사합니다!",
    date: "2시간 전",
    session: "프로덕트 전략",
  },
  {
    id: 2,
    mentee: "이준호",
    avatar: "https://images.unsplash.com/photo-1719400471588-575b23e27bd7?w=100",
    rating: 5,
    comment: "커리어 전환에 대한 고민을 해결할 수 있었어요. 친절하게 설명해주셔서 감사합니다.",
    date: "1일 전",
    session: "커리어 코칭",
  },
  {
    id: 3,
    mentee: "박서연",
    avatar: "https://images.unsplash.com/photo-1738750908048-14200459c3c9?w=100",
    rating: 5,
    comment: "실무 경험을 바탕으로 한 조언이 정말 도움이 되었습니다.",
    date: "2일 전",
    session: "스타트업 멘토링",
  },
];

export function RecentReviews() {
  return (
    <Card className="p-6 border-0 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="mb-1">최근 받은 리뷰</h3>
          <p className="text-gray-600 text-sm">멘티들의 피드백</p>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-1">
            <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            <span className="text-2xl">4.9</span>
          </div>
          <p className="text-gray-600 text-sm">평균 평점</p>
        </div>
      </div>

      <div className="space-y-4">
        {reviews.map((review) => (
          <div
            key={review.id}
            className="p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-start gap-3 mb-3">
              <ImageWithFallback
                src={review.avatar}
                alt={review.mentee}
                className="w-10 h-10 rounded-full object-cover"
              />
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span>{review.mentee}</span>
                    <span className="text-gray-400 text-sm">·</span>
                    <span className="text-gray-500 text-sm">{review.date}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: review.rating }).map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                    ))}
                  </div>
                </div>
                <p className="text-sm text-gray-500 mb-2">{review.session}</p>
                <p className="text-gray-700 text-sm">{review.comment}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
