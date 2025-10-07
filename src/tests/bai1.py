#Chuong2:Ham,module,packages
# Baitap1

def nhap(pr):
  n = int(input(pr))
  while n<0:
    print("Hay nhap nhap lai")
    n = int(input(pr))
  print(n)

def giaiThua(kq):
  if kq==0:
    return 1
  return kq * giaiThua(kq-1)


def xuat(n):
  print(n)
def main():
  n=nhap()
  res = giaiThua(n)
  xuat(res)

if __name__ == "__main__":
  main()