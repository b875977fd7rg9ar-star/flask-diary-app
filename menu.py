import add_file
import show_file
import delete_file
while True:
   print("メニューを選択してください")
   print("1.日記を書く")
   print("2.日記を読む")
   print("3.投稿を削除する")
   print("4.終了する")
   choise = input(">>")
   if choise == "1":
     add_file.write_file() 
   elif choise == "2":
     show_file.show_diary() 
   elif choise == "3":
     delete_file.delete_diary()
   elif choise == "4":
     print("終了します!")
     break 