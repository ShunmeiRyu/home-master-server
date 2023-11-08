from sshtunnel import SSHTunnelForwarder
 
server = SSHTunnelForwarder(
    ssh_address_or_host=('ec2-52-195-151-107.ap-northeast-1.compute.amazonaws.com', '22'),
    ssh_username='ec2-user',
    ssh_pkey = '~/.ssh/dev-01.pem', 
    remote_bind_address=('dev-01.c7ijk3ebddqr.ap-northeast-1.rds.amazonaws.com' , '5432'))
server.start()