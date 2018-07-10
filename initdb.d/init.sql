create table captions(
  hexdigest varchar(200) primary key,
  file_name varchar(200) not null,
  caption text not null,
  probablity float,
  created_at timestamp default NOW()
)
