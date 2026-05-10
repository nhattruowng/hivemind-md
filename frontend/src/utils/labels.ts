const valueLabels: Record<string, string> = {
  checking: "Đang kiểm tra",
  online: "Trực tuyến",
  offline: "Ngoại tuyến",
  healthy: "Hoạt động",
  ok: "Ổn định",
  success: "Thành công",
  failed: "Thất bại",
  running: "Đang chạy",
  pending: "Đang chờ",
  active: "Đang dùng",
  applied: "Đã áp dụng",
  rejected: "Đã từ chối",
  archived: "Đã lưu trữ",
  low: "Thấp",
  medium: "Trung bình",
  high: "Cao",
  prompt: "Lời nhắc",
  workflow: "Quy trình",
  tool: "Công cụ",
  error: "Lỗi",
  quick: "Nhanh",
  standard: "Tiêu chuẩn",
  deep: "Chuyên sâu",
  unknown: "Chưa rõ"
};

export function formatValueLabel(value?: string | null) {
  if (!value) return "Không có";
  const normalized = value.toLowerCase();
  return valueLabels[normalized] ?? value;
}
