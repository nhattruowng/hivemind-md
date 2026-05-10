# Knowledge Format

Mỗi lần build thành công tạo một file Markdown tại:

```txt
backend/knowledge/{{category}}/{{slug}}.md
```

Ví dụ:

```txt
backend/knowledge/ai-systems/local-multi-agent-architecture.md
```

## Format bắt buộc

```md
# {{title}}

## 1. Tóm tắt ngắn

## 2. Kiến thức chính

## 3. Chi tiết kỹ thuật

## 4. Quy trình hoặc kiến trúc

## 5. Ví dụ ứng dụng

## 6. Rủi ro và hạn chế

## 7. Nguồn tham khảo

## 8. Đánh giá độ tin cậy

## 9. Ngày cập nhật
```

## Metadata

SQLite lưu metadata trong bảng `knowledge_items`:

- `title`
- `slug`
- `category`
- `file_path`
- `sources`
- `trust_score`
- `created_at`
- `updated_at`

Vector metadata gồm `title`, `file_path`, `category`, `created_at`, `updated_at` và `sources`.

## Quy tắc đặt tên

- Topic được slugify thành chữ thường.
- Ký tự đặc biệt được đổi thành `-`.
- Category cũng được slugify để tạo thư mục.

