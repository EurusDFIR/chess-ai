# 🔧 Visual Studio 2022 - Cài đặt TỐI THIỂU cho C++ Engine

## ✅ Chỉ cần chọn những thứ này!

### **Workloads Tab:**

- ✅ **Desktop development with C++** ← Chỉ cần tick cái này!

### **Installation details (bên phải):**

#### **Included** (đã chọn sẵn - GIỮ NGUYÊN):

- ✅ C++ core desktop features
- ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
- ✅ C++ CMake tools for Windows
- ✅ Windows 11 SDK

#### **Optional** (BỎ HẾT - không cần!):

- ❌ C++ ATL for latest v143 build tools - BỎ TICK
- ❌ C++ Build Insights - BỎ TICK
- ❌ Just-In-Time debugger - BỎ TICK
- ❌ C++ profiling tools - BỎ TICK
- ❌ Test Adapter for Boost.Test - BỎ TICK
- ❌ Test Adapter for Google Test - BỎ TICK
- ❌ IntelliCode - BỎ TICK
- ❌ C++ AddressSanitizer - BỎ TICK
- ❌ vcpkg package manager - BỎ TICK
- ❌ GitHub Copilot - BỎ TICK
- ❌ C++ MFC for latest v143 - BỎ TICK
- ❌ C++ Modules for v143 - BỎ TICK
- ❌ Incredibuild - BỎ TICK

---

## 📊 Kích thước sau khi BỎ optional:

- **Trước:** ~8-10 GB
- **Sau khi bỏ optional:** ~3-4 GB
- **Download:** ~1.5 GB

---

## ⚡ Chỉ cần 4 thứ này:

1. ✅ **C++ core desktop features**
2. ✅ **MSVC v143 compiler** (x64/x86)
3. ✅ **C++ CMake tools**
4. ✅ **Windows 11 SDK**

**BỎ HẾT** các optional khác!

---

## 🚀 Sau khi cài xong:

```bash
# Restart VS Code
# Mở terminal mới và chạy:
python setup.py develop
```

Build sẽ mất ~2-5 phút.

---

## 💡 Nếu muốn nhẹ hơn nữa:

Thay vì cài Visual Studio, có thể chỉ cài **Build Tools**:

- Download: https://visualstudio.microsoft.com/downloads/
- Chọn: **Build Tools for Visual Studio 2022** (nhẹ hơn ~50%)
- Chỉ tick: **Desktop development with C++**
- Bỏ hết optional

**Build Tools** = Chỉ có compiler, không có IDE → nhẹ hơn!
