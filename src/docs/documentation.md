
## Tài liệu dự án Engine Cờ Vua AI

**1. Giới thiệu tổng quan**

Dự án này xây dựng một engine cờ vua AI sử dụng thuật toán Minimax với các kỹ thuật tối ưu hóa nâng cao để chơi cờ vua ở mức độ mạnh mẽ. Engine này bao gồm các thành phần chính sau:

* **Hàm đánh giá (Evaluation Function):**  Đánh giá chất lượng của một thế cờ cụ thể.
* **Thuật toán tìm kiếm (Search Algorithm):**  Tìm kiếm nước đi tốt nhất bằng cách khám phá cây trò chơi.
* **Kỹ thuật tối ưu hóa (Optimization Techniques):**  Nâng cao hiệu quả của thuật toán tìm kiếm và hàm đánh giá.
* **Sách khai cuộc (Opening Book):**  Sử dụng cơ sở dữ liệu khai cuộc để đi các nước đi khai cuộc đã được nghiên cứu.
* **Giao diện người dùng đồ họa (GUI):**  Giao diện đồ họa cho phép người dùng tương tác với engine cờ vua.

**2. Hàm đánh giá (Evaluation Function) - `src/ai/evaluation.py`**

**2.1. Tổng quan**

Hàm đánh giá là trái tim của engine cờ vua AI. Nó nhận một trạng thái bàn cờ làm đầu vào và trả về một giá trị số, thể hiện mức độ tốt của thế cờ đó đối với người chơi hiện tại. Giá trị dương cho thấy lợi thế cho người chơi Trắng, giá trị âm cho thấy lợi thế cho người chơi Đen, và giá trị gần 0 cho thấy thế cờ cân bằng.

**2.2. Các thành phần của hàm đánh giá**

Hàm `evaluate(board)` trong `src/ai/evaluation.py` kết hợp nhiều yếu tố để đưa ra đánh giá toàn diện về thế cờ:

* **Giá trị vật chất (Material Value):**
    * **Mô tả:**  Tính tổng giá trị quân cờ của mỗi bên. Mỗi loại quân được gán một giá trị cố định (`piece_values`).
    * **Triển khai:** Sử dụng từ điển `piece_values` để xác định giá trị của từng quân cờ (Tốt: 100, Mã: 320, Tượng: 330, Xe: 500, Hậu: 900, Vua: 20000).
    * **Lý do sử dụng:**  Vật chất là yếu tố cơ bản nhất để đánh giá thế cờ. Bên nào có nhiều quân hơn, đặc biệt là quân mạnh, thường có lợi thế lớn.

* **Bảng giá trị vị trí (Piece-Square Tables):**
    * **Mô tả:**  Gán thêm giá trị dựa trên vị trí của quân cờ trên bàn cờ. Các vị trí trung tâm và vị trí tốt cho từng loại quân sẽ có giá trị cao hơn (`position_values`).
    * **Triển khai:** Sử dụng từ điển `position_values` chứa các bảng giá trị cho từng loại quân. Giá trị được lấy từ bảng dựa trên ô vuông quân cờ đang đứng. Đối với quân Đen, bảng được "lật ngược" (`chess.square_mirror`) để phản ánh đúng vị trí tương đối.
    * **Lý do sử dụng:**  Vị trí quân cờ quan trọng không kém vật chất. Ví dụ, quân Mã ở trung tâm thường mạnh hơn ở góc bàn cờ. Bảng giá trị vị trí giúp engine nhận biết được điều này.

* **Tính cơ động (Mobility):**
    * **Mô tả:**  Đánh giá số lượng nước đi hợp lệ mà mỗi bên có. Bên nào có nhiều nước đi hợp lệ hơn thường linh hoạt và có nhiều lựa chọn hơn.
    * **Triển khai:** Tính số nước đi hợp lệ cho Trắng và Đen, sau đó lấy hiệu số và nhân với hệ số nhỏ (0.1).
    * **Lý do sử dụng:**  Mobility là một yếu tố quan trọng, đặc biệt trong trung cuộc và tàn cuộc. Mobility cao cho phép tạo ra nhiều mối đe dọa và hạn chế đối phương.

* **Kiểm soát trung tâm (Center Control):**
    * **Mô tả:**  Đánh giá mức độ kiểm soát các ô trung tâm (D4, E4, D5, E5). Kiểm soát trung tâm giúp kiểm soát bàn cờ và tạo điều kiện tấn công.
    * **Triển khai:** Đếm số ô trung tâm bị tấn công bởi mỗi bên, lấy hiệu số và nhân với hệ số nhỏ (0.1).
    * **Lý do sử dụng:**  Trung tâm bàn cờ là vị trí chiến lược quan trọng. Kiểm soát trung tâm giúp hạn chế quân đối phương và tạo bàn đạp cho các cuộc tấn công.

* **Phát triển quân (Piece Development):**
    * **Mô tả:**  Đánh giá mức độ phát triển quân cờ, đặc biệt là các quân nhẹ (Mã, Tượng). Phát triển quân sớm và hiệu quả giúp đưa quân vào vị trí hoạt động tốt.
    * **Triển khai:** Đếm số quân nhẹ của mỗi bên còn ở vị trí xuất phát ban đầu (B1, G1, C1, F1 cho Trắng và đối xứng cho Đen). Lấy hiệu số và nhân với hệ số nhỏ (0.1).
    * **Lý do sử dụng:**  Phát triển quân sớm là nguyên tắc khai cuộc quan trọng. Engine được khuyến khích phát triển quân nhanh chóng để tham gia vào cuộc chơi.

* **Tốt cô lập (Isolated Pawns):**
    * **Mô tả:**  Phạt điểm khi có tốt cô lập, tức là tốt không có tốt đồng minh nào ở các cột lân cận. Tốt cô lập thường yếu và dễ bị tấn công.
    * **Triển khai:**  Kiểm tra từng tốt, nếu không có tốt đồng minh ở cột bên cạnh thì trừ điểm (penalty = -50).
    * **Lý do sử dụng:**  Tốt cô lập là điểm yếu cấu trúc trong thế cờ. Engine được khuyến khích tránh tạo ra tốt cô lập.

* **An toàn vua (King Safety):**
    * **Mô tả:**  Đánh giá mức độ an toàn của vua. Vua bị tấn công nhiều sẽ bị trừ điểm.
    * **Triển khai:** Đếm số quân đối phương tấn công vua của mỗi bên, lấy hiệu số và nhân với hệ số âm (king_safety_weight = -50).
    * **Lý do sử dụng:**  An toàn vua là yếu tố sống còn trong cờ vua. Engine được khuyến khích giữ vua an toàn, đặc biệt trong trung cuộc và tàn cuộc.

* **Quân treo (Hanging Pieces Penalty):**
    * **Mô tả:** Phạt điểm khi có quân treo, tức là quân bị đối phương tấn công nhưng không được quân mình bảo vệ. Quân treo dễ bị mất không công.
    * **Triển khai:** Kiểm tra từng quân (trừ Vua), nếu bị đối phương tấn công nhưng không được quân mình bảo vệ thì trừ điểm (hanging_piece_penalty_weight = -50 nhân với giá trị quân).
    * **Lý do sử dụng:**  Tránh để quân treo là nguyên tắc cơ bản. Engine được khuyến khích bảo vệ quân của mình và tận dụng quân treo của đối phương.

* **Điểm tấn công tiềm năng (Attack Potential Score):**
    * **Mô tả:** Thưởng điểm cho khả năng tấn công vua đối phương.
    * **Triển khai:** Tính tổng giá trị quân của bên hiện tại đang tấn công vua đối phương (nhân với hệ số nhỏ 0.1 và sau đó nhân với attack_potential_weight = 5).
    * **Lý do sử dụng:**  Khuyến khích engine tạo ra các mối đe dọa tấn công vua đối phương.

* **Bảng cơ sở dữ liệu cờ tàn Syzygy (Syzygy Tablebases):**
    * **Mô tả:**  Sử dụng bảng cờ tàn Syzygy để đánh giá chính xác các thế cờ tàn có ít quân. Bảng Syzygy cung cấp kết quả thắng, hòa, thua (WDL - Win/Draw/Loss) cho mọi vị trí cờ tàn có đến 6 quân.
    * **Triển khai:**  Kiểm tra số lượng quân trên bàn cờ và quyền nhập thành. Nếu đủ điều kiện, sử dụng `chess.syzygy.open_tablebase` và `tablebase.probe_wdl` để lấy giá trị WDL từ bảng Syzygy. Giá trị WDL được nhân với một hệ số lớn (10000) để có trọng số cao trong đánh giá.
    * **Lý do sử dụng:**  Trong cờ tàn, việc đánh giá chính xác là rất quan trọng. Bảng Syzygy cung cấp độ chính xác tuyệt đối cho các thế cờ tàn nhất định, giúp engine chơi cờ tàn hoàn hảo trong những trường hợp này.

**2.3. Hàm `evaluate(board)`**

Hàm `evaluate(board)` tổng hợp tất cả các thành phần trên để tính toán điểm số cuối cùng cho thế cờ. Điểm số này được sử dụng bởi thuật toán tìm kiếm Minimax để đưa ra quyết định nước đi.

**3. Thuật toán tìm kiếm (Search Algorithm) - `src/ai/minimax.py`**

**3.1. Minimax với Alpha-Beta Pruning**

Engine sử dụng thuật toán **Minimax** làm nền tảng cho việc tìm kiếm nước đi tốt nhất. Minimax là một thuật toán tìm kiếm đối kháng được sử dụng trong lý thuyết quyết định, lý thuyết trò chơi, triết học và trí tuệ nhân tạo để giảm thiểu khả năng thua lỗ trong trường hợp xấu nhất.

Để tăng hiệu quả của Minimax, engine áp dụng kỹ thuật **Alpha-Beta Pruning**. Alpha-Beta Pruning là một kỹ thuật tối ưu hóa tìm kiếm giúp giảm số lượng nút cần duyệt trong cây trò chơi Minimax. Nó loại bỏ các nhánh cây không ảnh hưởng đến quyết định cuối cùng, giúp tìm kiếm nhanh hơn mà vẫn đảm bảo kết quả giống như Minimax thuần túy.

**3.2. Hàm `minimax(board, depth, alpha, beta, maximizing_player, killer_moves, history_heuristic_table, transposition_table)`**

* **Mô tả:** Hàm `minimax` triển khai thuật toán Minimax với Alpha-Beta pruning một cách đệ quy.
    * `board`: Trạng thái bàn cờ hiện tại.
    * `depth`: Độ sâu tìm kiếm còn lại.
    * `alpha`: Giá trị alpha hiện tại (giới hạn dưới tốt nhất mà bên Maximizing có thể đạt được).
    * `beta`: Giá trị beta hiện tại (giới hạn trên tốt nhất mà bên Minimizing có thể đạt được).
    * `maximizing_player`: `True` nếu lượt hiện tại là của bên Maximizing (Trắng), `False` nếu là bên Minimizing (Đen).
    * `killer_moves`: Từ điển lưu trữ "killer moves" cho từng độ sâu để tối ưu Move Ordering.
    * `history_heuristic_table`: Bảng History Heuristic để tối ưu Move Ordering.
    * `transposition_table`: Bảng chuyển vị để lưu trữ kết quả tìm kiếm đã tính toán.

* **Hoạt động:**
    1. **Kiểm tra Transposition Table:** Đầu tiên, hàm kiểm tra xem kết quả cho trạng thái bàn cờ hiện tại đã được lưu trong `transposition_table` hay chưa. Nếu có và độ sâu lưu trữ đủ lớn, hàm trả về kết quả đã lưu, giúp tránh tính toán lại.
    2. **Kiểm tra độ sâu và trạng thái kết thúc:** Nếu độ sâu tìm kiếm đạt 0 hoặc ván cờ đã kết thúc (chiếu hết, hòa), hàm gọi `quiescence_search` để đánh giá tĩnh thế cờ hiện tại.
    3. **Null Move Pruning:** Áp dụng Null Move Pruning để cắt tỉa các nhánh cây ít tiềm năng (nếu độ sâu đủ lớn và không bị chiếu).
    4. **Tìm kiếm Maximizing Player (Trắng):**
        * Duyệt qua các nước đi hợp lệ, được sắp xếp thứ tự bởi `order_moves`.
        * Gọi đệ quy `minimax` cho mỗi nước đi, giảm độ sâu đi 1 và đổi vai trò người chơi (sang Minimizing Player).
        * Cập nhật `max_eval` và `alpha` nếu tìm thấy giá trị đánh giá tốt hơn.
        * **Alpha-Beta Pruning:** Nếu `beta <= alpha`, cắt tỉa nhánh cây này vì không có khả năng cải thiện kết quả cho bên Maximizing. Lưu "killer move" nếu cắt tỉa xảy ra.
    5. **Tìm kiếm Minimizing Player (Đen):**
        * Tương tự như Maximizing Player, nhưng tìm `min_eval` và cập nhật `beta`.
        * **Alpha-Beta Pruning:** Nếu `beta <= alpha`, cắt tỉa nhánh cây này vì không có khả năng cải thiện kết quả cho bên Minimizing. Lưu "killer move" nếu cắt tỉa xảy ra.
    6. **Lưu kết quả vào Transposition Table:** Lưu giá trị đánh giá tốt nhất, độ sâu tìm kiếm và loại kết quả ('exact', 'lowerbound', 'upperbound') vào `transposition_table` để sử dụng lại trong tương lai.
    7. **Trả về giá trị đánh giá:** Trả về `max_eval` (cho Maximizing Player) hoặc `min_eval` (cho Minimizing Player).

**3.3. Hàm `get_best_move(board, depth)`**

* **Mô tả:** Hàm `get_best_move` là hàm giao diện để tìm nước đi tốt nhất cho một trạng thái bàn cờ nhất định.
    * `board`: Trạng thái bàn cờ hiện tại.
    * `depth`: Độ sâu tìm kiếm mong muốn.

* **Hoạt động:**
    1. **Khởi tạo:** Khởi tạo các biến cần thiết (`best_move`, `max_eval`, `killer_moves`, `history_heuristic_table`, `transposition_table`).
    2. **Iterative Deepening và Aspiration Windows:** Thực hiện tìm kiếm lặp lại sâu dần (`Iterative Deepening`) từ độ sâu 1 đến `depth`. Sử dụng `Aspiration Windows` để thu hẹp cửa sổ alpha-beta và tăng hiệu quả cắt tỉa.
    3. **Sắp xếp nước đi ban đầu:** Sử dụng `order_moves` để sắp xếp thứ tự các nước đi hợp lệ ở độ sâu đầu tiên.
    4. **Tìm kiếm song song (ThreadPoolExecutor):** Sử dụng `ThreadPoolExecutor` để thực hiện tìm kiếm Minimax song song cho từng nước đi ban đầu, giúp tận dụng sức mạnh đa nhân của CPU.
    5. **Chọn nước đi tốt nhất:**  Chọn nước đi có giá trị đánh giá cao nhất từ kết quả tìm kiếm song song.
    6. **Trả về nước đi tốt nhất:** Trả về nước đi tốt nhất tìm được.

**4. Kỹ thuật tối ưu hóa (Optimization Techniques) - `src/ai/minimax.py` và `src/ai/evaluation.py`**

**4.1. Zobrist Hashing**

* **Mô tả:** Kỹ thuật Zobrist Hashing được sử dụng để tạo ra một mã hash duy nhất cho mỗi trạng thái bàn cờ. Mã hash này được sử dụng để truy cập nhanh vào `transposition_table`.
* **Triển khai:**
    * **`zobrist_table`:** Một bảng hash Zobrist được khởi tạo ngẫu nhiên. Nó chứa các số ngẫu nhiên 64-bit cho mỗi quân cờ trên mỗi ô vuông, lượt đi, quyền nhập thành và ô phong tốt qua đường.
    * **`get_zobrist_hash(board)`:** Hàm này tính toán mã hash Zobrist cho một trạng thái bàn cờ cụ thể bằng cách XOR các số ngẫu nhiên tương ứng từ `zobrist_table` dựa trên vị trí quân cờ, lượt đi, quyền nhập thành và ô phong tốt qua đường.
* **Lý do sử dụng:** Zobrist Hashing giúp so sánh và lưu trữ các trạng thái bàn cờ một cách hiệu quả trong `transposition_table`, thay vì so sánh trực tiếp các đối tượng `chess.Board` phức tạp, giúp tăng tốc độ truy cập bảng chuyển vị.

**4.2. Transposition Table (Bảng chuyển vị)**

* **Mô tả:** `transposition_table` là một bảng (thường là hash table) dùng để lưu trữ kết quả tìm kiếm Minimax đã tính toán trước đó cho các trạng thái bàn cờ đã gặp.
* **Triển khai:**
    * `transposition_table = {}`: Bảng chuyển vị được khởi tạo là một từ điển Python rỗng.
    * Trong hàm `minimax`, trước khi thực hiện tìm kiếm, engine kiểm tra xem trạng thái bàn cờ hiện tại (`hash_value`) có trong `transposition_table` hay không. Nếu có và độ sâu lưu trữ đủ lớn, kết quả đã lưu được trả về trực tiếp.
    * Sau khi tính toán xong kết quả Minimax cho một trạng thái bàn cờ, kết quả này (giá trị đánh giá, độ sâu, loại kết quả) được lưu vào `transposition_table` với khóa là `hash_value`.
* **Lý do sử dụng:** Trong cờ vua, nhiều đường đi khác nhau có thể dẫn đến cùng một trạng thái bàn cờ (chuyển vị). Transposition Table giúp engine tránh việc tính toán lại giá trị Minimax cho các trạng thái đã được tính toán trước đó, tiết kiệm thời gian tính toán đáng kể và tăng độ sâu tìm kiếm hiệu quả.

**4.3. Move Ordering (Sắp xếp nước đi)**

* **Mô tả:** Kỹ thuật sắp xếp thứ tự các nước đi hợp lệ trước khi duyệt trong thuật toán Minimax. Mục tiêu là duyệt các nước đi "tốt" trước, để tăng khả năng Alpha-Beta Pruning cắt tỉa các nhánh cây vô ích.
* **Triển khai:**
    * **`order_moves(board, killer_moves_for_depth, history_heuristic_table)`:** Hàm này sắp xếp các nước đi hợp lệ dựa trên các heuristic sau:
        * **Killer Moves:** Các nước đi "killer" (thường gây ra cắt tỉa ở các nhánh cây khác) được ưu tiên duyệt trước.
        * **History Heuristic:** Các nước đi đã thành công trong việc tìm kiếm ở các vị trí tương tự trong quá khứ (được ghi lại trong `history_heuristic_table`) được ưu tiên.
        * **Nước chiếu:** Nước chiếu được ưu tiên cao.
        * **Nước bắt quân:** Nước bắt quân được ưu tiên (với điểm số MVV-LVA đơn giản).
        * **Nước phong cấp tốt:** Nước phong cấp tốt được ưu tiên.
    * **Static Exchange Evaluation (SEE) - `static_exchange_evaluation(board, move)`:**  (Đã được đề xuất thêm vào, chưa có trong code gốc) Đánh giá tĩnh trao đổi quân cho nước bắt quân để ưu tiên các nước bắt quân có lợi hơn.
    * **MVV-LVA (Most Valuable Victim - Least Valuable Attacker):** (Đã được đề xuất thêm vào, MVV-LVA score đã có trong `order_moves` hiện tại) Ưu tiên bắt quân có giá trị cao bằng quân có giá trị thấp.
* **Lý do sử dụng:** Move Ordering hiệu quả giúp Alpha-Beta Pruning cắt tỉa được nhiều nhánh cây hơn, từ đó engine có thể tìm kiếm sâu hơn trong cùng một khoảng thời gian, cải thiện đáng kể sức mạnh.

**4.4. Quiescence Search (Tìm kiếm tĩnh lặng)**

* **Mô tả:** Quiescence Search là một kỹ thuật tìm kiếm bổ sung được sử dụng ở các nút lá của cây tìm kiếm Minimax (khi đạt đến độ sâu giới hạn). Mục tiêu là giải quyết "horizon effect" - hiệu ứng đường chân trời, khi đánh giá tĩnh có thể bị sai lệch do bỏ qua các nước đi chiến thuật quan trọng ngay sau độ sâu tìm kiếm. Quiescence Search tiếp tục tìm kiếm sâu hơn chỉ đối với các nước đi "động" (thường là nước bắt quân, nước chiếu, nước phong cấp) cho đến khi đạt được trạng thái "tĩnh lặng" (quiescent position), tức là vị trí mà giá trị đánh giá không thay đổi đáng kể trong một vài nước đi tiếp theo.
* **Triển khai:**
    * **`quiescence_search(board, alpha, beta, transposition_table)`:** Hàm này thực hiện Quiescence Search.
        * Đầu tiên, nó kiểm tra Transposition Table.
        * Sau đó, nó đánh giá tĩnh thế cờ hiện tại (`stand_pat = evaluate(board)`).
        * Nếu `stand_pat` vượt quá `beta`, trả về `beta` (cắt tỉa beta).
        * Nếu `stand_pat` lớn hơn `alpha`, cập nhật `alpha`.
        * Sau đó, nó chỉ xem xét các nước bắt quân hợp lệ và gọi đệ quy `quiescence_search` cho các nước đi này.
        * Kết quả tốt nhất tìm được được trả về.
* **Lý do sử dụng:** Quiescence Search giúp cải thiện độ chính xác của đánh giá ở các nút lá, đặc biệt trong các tình huống chiến thuật, giúp engine tránh bỏ sót các cơ hội chiến thuật hoặc rơi vào bẫy.

**4.5. Null Move Pruning**

* **Mô tả:** Null Move Pruning là một kỹ thuật cắt tỉa mạnh mẽ, dựa trên ý tưởng rằng nếu bỏ qua lượt đi (thực hiện "null move") vẫn dẫn đến giá trị quá thấp (vượt quá beta), thì các nước đi thông thường cũng không có khả năng cải thiện kết quả, do đó có thể cắt tỉa nhánh cây này.
* **Triển khai:**
    * **`null_move_pruning(board, depth, alpha, beta, transposition_table)`:** Hàm này thực hiện Null Move Pruning.
        * Nó kiểm tra điều kiện áp dụng (độ sâu đủ lớn và không bị chiếu).
        * Nếu đủ điều kiện, nó thực hiện "null move" (bỏ qua lượt đi) và gọi đệ quy `minimax` với độ sâu giảm đi (depth - 1 - R, với R thường là 2).
        * Nếu giá trị trả về từ tìm kiếm Null Move lớn hơn hoặc bằng `beta`, nó trả về `beta` (cắt tỉa beta).
* **Lý do sử dụng:** Null Move Pruning là một kỹ thuật cắt tỉa hiệu quả, giúp giảm đáng kể số lượng nút cần duyệt, đặc biệt trong trung cuộc. Tuy nhiên, cần cẩn thận khi sử dụng Null Move Pruning trong cờ tàn và các tình huống đặc biệt, vì nó có thể dẫn đến lỗi trong một số trường hợp.

**4.6. Iterative Deepening (Tìm kiếm lặp lại sâu dần)**

* **Mô tả:** Iterative Deepening là kỹ thuật bắt đầu tìm kiếm ở độ sâu nhỏ (ví dụ: 1), sau đó tăng dần độ sâu (2, 3, 4, ...). Kết quả tìm kiếm từ độ sâu trước được sử dụng để cải thiện Move Ordering ở độ sâu hiện tại.
* **Triển khai:**
    * **`get_best_move(board, depth)`:** Hàm `get_best_move` triển khai Iterative Deepening bằng cách lặp qua các độ sâu từ 1 đến `depth`.
    * Ở mỗi độ sâu, nó gọi hàm `minimax` để thực hiện tìm kiếm.
    * Kết quả tốt nhất từ độ sâu trước (nước đi tốt nhất) được sử dụng để sắp xếp nước đi ở độ sâu hiện tại (thông qua Move Ordering, Killer Moves, History Heuristic).
* **Lý do sử dụng:**
    * **Kiểm soát thời gian:** Iterative Deepening cho phép engine trả về nước đi tốt nhất ngay cả khi hết thời gian tính toán giữa chừng (nước đi tốt nhất ở độ sâu nông hơn vẫn có thể sử dụng được).
    * **Cải thiện Move Ordering:** Kết quả từ độ sâu nông hơn giúp sắp xếp nước đi hiệu quả hơn ở độ sâu sâu hơn, tăng hiệu quả Alpha-Beta Pruning.
    * **Aspiration Windows:** Iterative Deepening thường được kết hợp với Aspiration Windows.

**4.7. Aspiration Windows (Cửa sổ kỳ vọng)**

* **Mô tả:** Aspiration Windows là kỹ thuật thu hẹp cửa sổ Alpha-Beta ban đầu xung quanh giá trị đánh giá tốt nhất từ lần tìm kiếm ở độ sâu trước (trong Iterative Deepening). Nếu kết quả tìm kiếm nằm ngoài cửa sổ này (fail-high hoặc fail-low), tìm kiếm lại với cửa sổ rộng hơn.
* **Triển khai:**
    * **`get_best_move(board, depth)`:** Hàm `get_best_move` triển khai Aspiration Windows.
    * Ở mỗi độ sâu (sau độ sâu 1), nó thiết lập cửa sổ alpha-beta ban đầu dựa trên giá trị đánh giá tốt nhất từ độ sâu trước (`best_eval`).
    * Nếu kết quả tìm kiếm (`current_best_eval`) nằm ngoài cửa sổ (<= alpha hoặc >= beta), nó mở rộng cửa sổ và có thể thực hiện tìm kiếm lại (trong code mẫu, việc tìm kiếm lại được bỏ qua để đơn giản, nhưng nên triển khai trong thực tế).
* **Lý do sử dụng:** Aspiration Windows có thể tăng tốc độ tìm kiếm trong trường hợp giá trị đánh giá không thay đổi quá nhiều giữa các lần lặp độ sâu, vì cửa sổ hẹp hơn làm tăng khả năng Alpha-Beta Pruning cắt tỉa.

**4.8. Killer Moves**

* **Mô tả:** Killer Moves là các nước đi đã gây ra cắt tỉa beta (beta cutoff) trong quá trình tìm kiếm ở các nhánh cây khác. Chúng thường là các nước đi mạnh và có khả năng tốt trong các vị trí tương tự.
* **Triển khai:**
    * **`killer_moves`:** Một từ điển `killer_moves` được sử dụng để lưu trữ killer moves cho từng độ sâu. Khi một nước đi gây ra beta cutoff trong hàm `minimax`, nó được thêm vào danh sách killer moves cho độ sâu hiện tại.
    * **`order_moves(board, killer_moves_for_depth, history_heuristic_table)`:** Trong hàm `order_moves`, killer moves được ưu tiên duyệt trước.
* **Lý do sử dụng:** Killer Moves giúp Move Ordering hiệu quả hơn bằng cách ưu tiên các nước đi có tiềm năng tốt, tăng khả năng cắt tỉa Alpha-Beta.

**4.9. History Heuristic**

* **Mô tả:** History Heuristic là một kỹ thuật học hỏi kinh nghiệm từ các lần tìm kiếm trước. Nó ghi lại tần suất thành công của mỗi nước đi (dựa trên ô đi và ô đến) trong việc cải thiện giá trị đánh giá. Các nước đi có "lịch sử" thành công tốt hơn được ưu tiên duyệt trước trong Move Ordering.
* **Triển khai:**
    * **`history_heuristic_table`:** Một bảng hash `history_heuristic_table` (defaultdict) được sử dụng để lưu trữ điểm số History Heuristic cho mỗi cặp ô (ô đi, ô đến).
    * **Cập nhật History Heuristic:**
        * Trong hàm `minimax`, khi một nước đi được chọn là nước đi tốt nhất, điểm số History Heuristic của nước đi đó được tăng lên (ví dụ: cộng thêm `math.log(depth + 1)` hoặc `depth*depth*2` nếu gây cutoff).
        * Trong hàm `order_moves`, điểm số History Heuristic được sử dụng để sắp xếp thứ tự các nước đi.
* **Lý do sử dụng:** History Heuristic giúp Move Ordering thích nghi với đặc điểm của từng vị trí cụ thể và học hỏi từ kinh nghiệm tìm kiếm trước đó, cải thiện hiệu quả cắt tỉa Alpha-Beta theo thời gian.

**5. Sách khai cuộc (Opening Book) - `src/ai/opening_book.py`**

* **Tổng quan:** Engine sử dụng sách khai cuộc để đi các nước đi khai cuộc đã được chuẩn bị trước, thay vì tìm kiếm bằng thuật toán Minimax ở giai đoạn khai cuộc.
* **Triển khai:**
    * **`OpeningBook` class:** Lớp `OpeningBook` trong `src/ai/opening_book.py` quản lý việc đọc và truy xuất nước đi từ sách khai cuộc.
    * **`BOOK_PATH`:** Đường dẫn đến file sách khai cuộc (ví dụ: `gm2600.bin`).
    * **`OpeningBook.get_move(board)`:** Hàm này tìm kiếm nước đi khai cuộc phù hợp cho trạng thái bàn cờ hiện tại trong sách khai cuộc. Nếu tìm thấy, nó trả về nước đi đó; nếu không, trả về `None`.
* **Lý do sử dụng:**
    * **Đi khai cuộc mạnh:** Sách khai cuộc chứa các nước đi khai cuộc đã được nghiên cứu và kiểm chứng bởi các chuyên gia cờ vua, giúp engine đi khai cuộc mạnh mẽ và tránh các sai lầm sớm.
    * **Tiết kiệm thời gian:** Sử dụng sách khai cuộc giúp tiết kiệm thời gian tính toán ở giai đoạn khai cuộc, cho phép engine tập trung vào tìm kiếm sâu hơn ở trung cuộc và tàn cuộc.

**6. Giao diện người dùng đồ họa (GUI) - `src/gui/main_window.py`**

* **Tổng quan:** Giao diện đồ họa được xây dựng bằng Pygame, cho phép người dùng chơi cờ vua với engine AI.
* **Các hàm chính:**
    * **`run_gui()`:** Hàm khởi tạo và chạy vòng lặp chính của giao diện GUI.
    * **`draw_board()`:** Vẽ bàn cờ lên màn hình.
    * **`draw_pieces()`:** Vẽ quân cờ lên bàn cờ.
    * **`load_pieces()`:** Tải hình ảnh quân cờ từ thư mục assets.
    * **`handle_mouse_click(pos)`:** Xử lý sự kiện click chuột của người dùng (chọn quân, di chuyển quân).
    * **`ai_move()`:** Gọi hàm `get_best_move` để AI di chuyển và cập nhật bàn cờ.

**7. Ứng dụng chính (Main Application) - `src/main.py`**

* **Tổng quan:** File `src/main.py` là điểm khởi đầu của ứng dụng.
* **Triển khai:**
    * Gọi hàm `run_gui()` từ `src/gui/main_window.py` để khởi chạy giao diện đồ họa và bắt đầu trò chơi.

**8. Kết luận**

Engine cờ vua AI này đã tích hợp nhiều thuật toán và kỹ thuật mạnh mẽ để đạt được hiệu suất chơi cờ tốt. Các kỹ thuật như Minimax với Alpha-Beta Pruning, Transposition Table, Move Ordering, Quiescence Search, Null Move Pruning, Iterative Deepening, Aspiration Windows, Killer Moves, History Heuristic, và sách khai cuộc đều đóng vai trò quan trọng trong việc nâng cao sức mạnh và hiệu quả của engine.

**Các hướng cải tiến tiềm năng:**

* **Neural Network Evaluation (NNUE):** Thay thế hàm đánh giá tĩnh hiện tại bằng mạng nơ-ron NNUE để đánh giá thế cờ chính xác và tinh tế hơn.
* **Monte Carlo Tree Search (MCTS):** Nghiên cứu và tích hợp MCTS để kết hợp ưu điểm của MCTS với Alpha-Beta, hoặc thử nghiệm engine hoàn toàn dựa trên MCTS.
* **Tối ưu hóa hiệu năng:** Tiếp tục tối ưu hóa code, đặc biệt là các hàm tìm kiếm và đánh giá, để engine có thể tìm kiếm sâu hơn trong cùng một khoảng thời gian.
* **Học máy:**  Áp dụng các kỹ thuật học máy để tự động tinh chỉnh các hệ số đánh giá, hoặc huấn luyện các mô hình đánh giá phức tạp hơn.
