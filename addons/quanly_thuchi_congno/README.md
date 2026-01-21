Quản lý Thu Chi & Công nợ

Mục tiêu:
- Quản lý `Phiếu Thu` (`phieu_thu`) và `Phiếu Chi` (`phieu_chi`)
- Quản lý `Công nợ phải thu` và `Công nợ phải trả`
- Mở rộng `res.partner` với trường `is_doi_tac` và quan hệ công nợ

Tích hợp:
- Khi `thanh_ly_tai_san` có `hanh_dong='ban'` và `gia_ban>0`, tự động tạo `phieu_thu` và liên kết qua `phieu_thu_id`.
- Nếu `muon_tra_tai_san` có `phi>0`, tự động tạo `phieu_thu` cho phí và liên kết qua `phieu_thu_id`.

Hướng dẫn nhanh:
- Cài module `quanly_thuchi_congno`.
- Kiểm tra menu `Thu Chi & Công nợ` ở menu chính.

Lưu ý:
- Đây là triển khai tối thiểu ban đầu; nếu muốn ghi sổ kế toán tự động (journal entries), cần tích hợp thêm với `account` và quy tắc kế toán.