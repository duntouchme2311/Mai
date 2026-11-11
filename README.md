# Mai: Game du lịch 3D (prototype)

Thử nghiệm làm game **du lịch ảo 3D chạy trên trình duyệt**: người chơi dạo quanh một địa danh thật, làm nhiệm vụ khám phá, trả lời câu hỏi, chụp ảnh lưu niệm và nhận xu.

Bản đầu tiên (vertical slice): **Nhà thờ Đức Bà, TP. Hồ Chí Minh**, file `game/index.html`.

## Chạy thử

Mở `game/index.html` trên trình duyệt (cần internet để tải Three.js từ CDN), hoặc chạy:

```bash
npx serve game   # rồi mở http://localhost:3000
```

| Thao tác | Máy tính | Điện thoại |
|---|---|---|
| Di chuyển | WASD / mũi tên | Joystick trái |
| Chạy | Shift | Nút "Chạy" |
| Xoay camera | Kéo chuột | Vuốt màn hình |
| Tương tác | E | Nút vàng |

## Những gì đã có

- Thế giới 3D dựng hoàn toàn bằng code (low-poly): nhà thờ có 2 tháp chuông, cửa sổ hoa hồng, đồng hồ, hàng rào và cổng; tượng Đức Mẹ, quảng trường, đường phố, cây, các khối nhà xung quanh.
- Nhân vật góc nhìn thứ ba, có va chạm, cùng 24 NPC đi dạo.
- HUD: minimap, vị trí, giờ trong game, ví xu, danh sách nhiệm vụ.
- 3 nhiệm vụ: tìm 5 chi tiết đặc trưng (cột sáng), quiz 4 câu với hướng dẫn viên, chụp và tải ảnh lưu niệm.
- Điều khiển được cả máy tính lẫn điện thoại. Không cần asset ngoài; chỉ phụ thuộc Three.js r160.

## Phân tích tham chiếu (vietnam3d.online)

Ảnh chụp bài đăng cho thấy một sản phẩm cùng thể loại: **web 3D du lịch ảo** với HUD nhiệm vụ, ví tiền ảo, mảnh ghép/bộ sưu tập, bản đồ.
Tôi chưa truy cập được trang đó, nên **chưa xác minh** họ dùng engine gì (Unity WebGL, Three.js/Babylon.js hay PlayCanvas). Dự án này chỉ làm cùng thể loại và cơ chế, không sao chép giao diện hay nội dung của họ.

**Rủi ro lớn nhất không nằm ở code mà ở asset 3D địa danh.** Dựng một địa danh giống thật mất nhiều thời gian nhất (photogrammetry, mua model, hoặc thuê dựng). Prototype này né vấn đề bằng cách dựng low-poly bằng code.

## Lộ trình đề xuất

| Giai đoạn | Mục tiêu | Việc chính | Cần quyết định |
|---|---|---|---|
| 0. Prototype (xong) | Cảm giác chơi trên web, cả mobile | 1 địa danh, 3 nhiệm vụ | Có đúng hướng muốn làm không? |
| 1. MVP | Cho 20–50 người chơi thử | Model 3D thật hơn (GLB), âm thanh, lưu tiến trình, 2–3 địa danh khu Q1 (Bưu điện, Nhà hát) | Nguồn asset: tự dựng / mua / photogrammetry |
| 2. Nội dung | Giữ chân người chơi | Bộ sưu tập, mảnh ghép, bảng xếp hạng, nhiều thành phố | Mô hình kiếm tiền: quảng cáo du lịch, B2B (sở du lịch, trường học), vé |
| 3. Nền tảng | Mở rộng | Multiplayer, CMS để nhập điểm đến và quiz không cần code | Tiếp tục Three.js hay chuyển sang Unity |

## Ghi chú

- Các thông tin lịch sử trong game (năm khánh thành 1880, gạch Marseille, tượng 1959, tháp khoảng 60 m) lấy từ nguồn công khai phổ biến; nên đối chiếu lại trước khi phát hành.
- `window.__game` là hook để test tự động, có thể bỏ khi phát hành.
