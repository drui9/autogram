from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	email = Column(String, unique=True)
	order = relationship('Order', back_populates='user')

class Order(Base):
	__tablename__ = 'order'

	id = Column(Integer, primary_key=True)
	total = Column(Integer)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship('User', back_populates='order')

	@classmethod
	def change_total(cls, engine, value):
		with Session(bind=engine) as session:
			order = session.query(cls).first()
			print(order.total)
			order.total = value
			print(order.total)


def main():
	# prepare engine
	engine = create_engine('sqlite:///:memory:', echo=False)
	Base.metadata.create_all(engine)
	#
	user = User()
	user.name = 'John Doe'
	user.email = 'johndoe@gmail.com'

	order = Order()
	order.total = 200.0
	order.user = user

	with Session(bind=engine) as session:
		session.add(user)
		session.commit()

	# attempt change
	Order.change_total(engine, 300)
	# with Session(bind=engine) as session:
	# 	the_order = session.query(Order).first()
	# 	the_order.total = 300
	# 	session.commit()
	# with Session(bind=engine) as session:
	# 	the_order = session.query(Order).first()
	# 	print(the_order.total)

	print('--end--')
