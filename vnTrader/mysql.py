# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtWidgets, QtSql
import sys

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QTableView()
window.setWindowTitle("QSqlQueryModel")
# 创建数据库连接
con = QtSql.QSqlDatabase.addDatabase('QMYSQL')
con.setHostName('localhost')
con.setPort(3306)
con.setDatabaseName('stock')
con.setUserName('root')
con.setPassword('123456')
con.open()
# 创建SQL模型
# model = QtSql.QSqlTableModel(parent=window)
# model.setTable("user")
sqm = QtSql.QSqlQueryModel(parent=window)
sqm.setQuery('select * from stock.account')
# sqm.setQuery('select * from stock.account')
# sqm.setQuery('SELECT * FROM stock.holding_stock_detail_current')
# 设置模型的标题栏
# sqm.setHeaderData(1, QtCore.Qt.Horizontal, '名字')
# sqm.setHeaderData(2, QtCore.Qt.Horizontal, '数量')
# 将查询结果与表组件关联
sqm.setQuery('SELECT * FROM stock.holding_stock_detail_current')
# window.setModel(model)
window.setModel(sqm)

# 隐藏第一列
# window.hideColumn(0)
# sqm.setTable('good')
# window.setHorizontalHeader()
window.setColumnWidth(1, 150)
window.setColumnWidth(2, 60)
window.resize(230, 130)
window.show()


# setWindowTitle('mySqlQueryModel')
sys.exit(app.exec_())

# QSqlQueryModel *model = new QSqlQueryModel;
#     model->setQuery(“select * from student”);
#     model->setHeaderData(0, Qt::Horizontal, tr(“id”));
#     model->setHeaderData(1, Qt::Horizontal, tr(“name”));
#     QTableView *view = new QTableView;
#     view->setModel(model);
#     view->show();
#     MySqlQueryModel *myModel = new MySqlQueryModel; //创建自己模型的对象
#     myModel->setQuery(“select * from student”);
#     myModel->setHeaderData(0, Qt::Horizontal, tr(“id”));
#     myModel->setHeaderData(1, Qt::Horizontal, tr(“name”));
#     QTableView *view1 = new QTableView;
#     view1->setWindowTitle(“mySqlQueryModel”); //修改窗口标题
#     view1->setModel(myModel);
#     view1->show();
# }

## Connect and check connection state
# def _trytoConnect(self):
#     if (self.db.open()):
#         print "Success"
#     else:
#         print "Failed to connect to mysql"