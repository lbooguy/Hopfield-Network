import sys
import numpy as np
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QCoreApplication
from PyQt5.Qt import *

GDATA=[] #глобальный массив данных, который будет передан в дочерний класс для реализации кнопки "просмотреть образы"
GSizeGridle=0 #глобальный размер сетки кнопок для рисования аналогичный верхней переменной
class Network(QWidget):
    SizeGridle=12
    global GSizeGridle
    GSizeGridle=SizeGridle
    Square_SizeGridle=SizeGridle*SizeGridle #квадрат размера
    DATA=np.zeros((1,Square_SizeGridle)) #основной массив образов памяти, который будет использован в программе
    count=0#счетчик образов
    def __init__(self):
        super().__init__()     
        self.DRAW_ARRAY=np.zeros(self.Square_SizeGridle,dtype=np.float32)#массив, который будет заполняться единицами по мере заполнения поля для рисования
        self.W=np.zeros((self.Square_SizeGridle,self.Square_SizeGridle),dtype=np.float32)#матрица весов
        self.initUI()
       
 
    def Fill(self):#метод меняющий цвет кнопки на красный и изменяющий значений DRAW_ARRAY
            sender = self.sender()# информация о кпопке отправителе
            for i in range(self.Square_SizeGridle):
                 if sender==self.buttons[i]:#если эта кнопка совпадает с одной i-той кпопкой в массиве кнопок то соответсвенно меняется значение DRAW_ARR                     self.DRAW_ARRAY[i]=1
            sender.setStyleSheet('QPushButton {background-color: red; color: white;}')   #изменение цвета отправителя


    def Clear(self):#метод очищающий поле для рисования
        for i in range(self.Square_SizeGridle):
            self.buttons[i].setStyleSheet('QPushButton {background-color:  ; color: red;}')#изменение цвета всех кнопок на стандартный
        self.DRAW_ARRAY=np.zeros(self.Square_SizeGridle,dtype=np.float32)#обнуление DRAW_ARR                
                
    def Inizialization(self):#запись в память набранного на поле образа
        self.DATA[self.count]=self.DRAW_ARRAY#сама запись
        self.DATA[self.count]=np.resize(self.DATA[self.count],(1,self.Square_SizeGridle))
        self.count+=1#+ 1 образ
        self.DATA=np.resize(self.DATA,(self.count+1,self.Square_SizeGridle))#изменение размера матрицы для следующего образа
        #при таком способе записи в память последним будет записан еще один массив, который будет равен первому,поэтому для корректного использования
        #величины len(self.DATA) необходимо из нее вычитать единицу, чтобы убрать последний неактуальный массив
        self.Clear()#при окончании записи поле очищается 

    

    def Learning(self):#обучение нейросети

        for i in range(len(self.DATA)-1):#цикл вычисляющий матрицу весов
                X=np.resize(self.DATA[i],(1,len(self.DATA[i])))
                XT=np.resize(self.DATA[i],(len(self.DATA[i]),1))#транспонирование X           
                self.W =self.W+ XT.dot(X)  
        self.W=self.W/self.Square_SizeGridle#нормировка
        for i in range(self.Square_SizeGridle):
            for j in range(self.Square_SizeGridle):
                if i==j:
                    self.W[i][j] = 0#обнуление диагонали
        self.Clear()
        

    def ShowResult(self,Arr):#метод , который вызывается в случае успешного использования нейросети
            for i in range(self.Square_SizeGridle):#показывает найденный образ
                if Arr[i]==1:
                 self.buttons[i].setStyleSheet('QPushButton {background-color: red; color: white;}')
                else:
                 self.buttons[i].setStyleSheet('QPushButton {background-color:  ; color: red;}')


    def Search(self):  #использование нейросети
        Y2=self.DRAW_ARRAY#по сути этот метод берет в аргумент массив DRAW_ARRAY
        F=self.DRAW_ARRAY
        for t in range(1000):  #количество итераций при которых сеть будет пытаться отыскать образ
            Y2T=np.resize(self.DRAW_ARRAY,(len(self.DRAW_ARRAY),1))#транспонирование Y2T
            d=np.dot(self.W,Y2T)
            for j in range(len(self.DRAW_ARRAY)):   
                if d[j]>0:
                    Y2[j]=1
                else:
                    Y2[j]=0
            for i in range(len(self.DATA)-1):#если сеть найдет образ то вызывается метод ShowResult 
                if np.array_equal(self.DATA[i], Y2):
                    self.ShowResult(self.DATA[i])
                    return 0
                else:        
                    self.DRAW_ARRAY=Y2
        #если сеть не обнаружила результат за 1000 итераций то появляется следующее сообщение:           
        #ОБРАБОТКА РЕЗУЛЬТАТА В СЛУЧАЕ НЕУДАЧНОГО ПОИСКА
        msg = QMessageBox()
        msg.setWindowTitle("Результат работы")
        msg.setText("Сеть пришла к состоянию, которого нет в памяти")
        msg.setIcon(QMessageBox.Information)
        msg.setWindowIcon(QIcon('DigitalBrain.jpg'))
        x = msg.exec_()
        self.Clear()

        
    def ClearMemory(self):#очистка памяти от записанных образов-простое обнуление всех массивов и счетчика образов
         global GDATA 
         GDATA=[]
         self.DATA=np.zeros((1,self.Square_SizeGridle))
         self.W=np.zeros((self.Square_SizeGridle,self.Square_SizeGridle),dtype=np.float32)
         self.Clear()
         self.count=0

    def ShowContents(self):#метод показывающий все записанные в память образы
        global GDATA
        GDATA=self.DATA
        self.childwin = ChildWin()#вызов дочернего окна
        self.childwin.show()
        self.DATA=GDATA


    def initUI(self):
        n=45*self.SizeGridle+5 #константа выравнивания кнопок управления по левому краю
        self.buttons=[] #массив кнопок рисования
        
        #КНОПКА "ЗАПОМНИТЬ ОБРАЗ"
        SaveButton = QPushButton('Запомнить образ', self)
        SaveButton.resize(150,30)
        SaveButton.move(n,  10)
        SaveButton.clicked.connect(self.Inizialization)
            
        #КНОПКА "ЗАКОНЧИТЬ ЗАПОМИНАНИЕ"
        EndButton = QPushButton('Обучить нейросеть', self)
        EndButton.resize(150,30)
        EndButton.move(n, 40)
        EndButton.clicked.connect(self.Learning)

    
        #КНОПКА "ПРОСМОТРЕТЬ ОБРАЗ"
        LookButton = QPushButton('Просмотреть образы', self)
        LookButton.resize(150,30)
        LookButton.move(n, 70)
        LookButton.clicked.connect(self.ShowContents)

        #КНОПКА "ПОИСК"
        SearchButton = QPushButton('Начать поиск', self)
        SearchButton.resize(150,30)
        SearchButton.move(n, 100)
        SearchButton.clicked.connect(self.Search)

        #КНОПКА "ОЧИСТИТЬ ПОЛЕ"
        ClearButton = QPushButton('Очистить поле', self)
        ClearButton.resize(150,30)
        ClearButton.move(n, 130)
        ClearButton.clicked.connect( self.Clear)
        
        #КНОПКА "ОЧИСТИТЬ ПАМЯТЬ"
        SearchButton = QPushButton('Очистить память', self)
        SearchButton.resize(180,60)
        SearchButton.move(n, 200)
        SearchButton.clicked.connect(self.ClearMemory)

        
        #КНОПКИ СЕТКИ РИСУНКА
        for j in range(self.SizeGridle):
             for i in range(self.SizeGridle):
                btn = QPushButton('', self)
                btn.resize(45,45)
                btn.move(45*i, 45*j)
                btn.clicked.connect( self.Fill)
                self.buttons.append(btn)
                
        
        #ПАРАМЕТРЫ ОКНА
        self.setGeometry(10,50,45*self.SizeGridle+205, 45*self.SizeGridle+5)
        self.setWindowTitle('HOPFIELD NETWORK')
        self.setWindowIcon(QIcon('DigitalBrain.jpg'))# некоторое изображение в папке с этим файлом
        self.show()

        
class ChildWin(Network): #дочернее окно
    def __init__(self, parent=None):
        #super().__init__()
        QWidget.__init__(self,parent)
        
        #ПАРАМЕТРЫ ОКНА С ОБРАЗАМИ
        self.setGeometry(150,150,900, 500)
        self.setWindowTitle('RES')
        self.setWindowIcon(QIcon('DigitalBrain.jpg'))
        
        global GDATA
        H_Arr=GDATA
        
        SQ=GSizeGridle*GSizeGridle
        BUTT=[[0]*SQ for i in range(len(H_Arr)-1)]#массив всех кнопок
        l=0#счетчик элементов массива кнопок
        for k in range(len(H_Arr)-1):
            for j in range(GSizeGridle):
                for i in range(GSizeGridle):
                    
                     #КНОПКИ СЕТКИ ОБРАЗОВ
                     g = QPushButton('', self)
                     g.resize(15,15)
                     g.move(14*i+16*GSizeGridle*k+10, 14*j)
                     
                     BUTT[k][l]=g#запись ВСЕХ кнопок для рисования в массив
                     l=l+1
            for p in range(SQ):
                if H_Arr[k][p]==1:#изменение цвета кнопки для которой элемент массива данных равен 1
                    BUTT[k][p].setStyleSheet('QPushButton {background-color: red; color: white;}')
            l=0
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Network()
    sys.exit(app.exec_())
    


