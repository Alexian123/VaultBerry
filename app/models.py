from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class VaultEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    url = db.Column(db.String(255), unique=True, nullable=True)
    encrypted_username = db.Column(db.String(255), unique=True, nullable=False)
    encrypted_password = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f'<VaultEntry {self.url} for User {self.user_id}>'