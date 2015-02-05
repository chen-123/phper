#!/user/bin/perl
# add by chen-123 @phpdba 2013
# xml配置文件将需要监控的master与slave列表，名称、地址、端口、帐号、密码设置好。
use warnings;
use strict;
use DBI;
use Net::SMTP;
#use Net::SMTP_AUTH;
#use MIME::Base64;
use IO::Socket;
use XML::Simple;
use Time::HiRes;
use POSIX "strftime";
#use Data::Dumper;

my $simple;
my $xml;
my @data;
my ($M_dbh,$S_dbh,$M_connect,$S_connect);
my %ip_port_list;
my $app_name;
my $today = strftime("%Y-%m-%d",localtime(time));

my $check_log = 'mysql_check_log/mysql_replication_log'.strftime("%Y-%m-%d",localtime(time)).'.txt';
my $open_check_log = 'yes';
my $default_seconds_behind_limit = 20;
my $master_slave_table_diff_size = 30;
my $send_email_status = 0;
my $debug_print = 1;

my ($master_monitor_user,$master_monitor_pass,$master_monitor_db,$master_ip,$master_db_port,$master_type,$master_name);
my ($slave_monitor_user,$slave_monitor_pass,$slave_monitor_db,$slave_ip,$slave_db_port,$slave_type,$slave_name);

$simple = XML::Simple->new();
my $data   = $simple->XMLin('db_master_slave_config.xml');
my $tmp = $data->{server};
my @kk = keys(%$tmp);
foreach my $kv (@kk){
        print $kv."\n";
        my $master_list = $tmp->{$kv}->{master_list}->{master};
        my $slave_list = $tmp->{$kv}->{slave_list}->{slave};

        if($master_list->{name}){
                $master_monitor_user = $master_list->{monitor_user};
                $master_monitor_pass = $master_list->{monitor_pass};
		$master_monitor_db = $master_list->{monitor_db};
                $master_ip = $master_list->{ip};
                $master_db_port = $master_list->{port};
                $master_type = $master_list->{type};
                $master_name = $master_list->{name};
                #print "$master_name -> $master_type -> $master_monitor_db -> $master_ip -> $master_db_port ->$master_monitor_user -> $master_monitor_pass \n";
        }else{
                foreach my $k_ml ( keys(%$master_list)){
                        if(ref($master_list->{$k_ml}) eq "HASH"){
                                $master_monitor_user = $master_list->{$k_ml}->{monitor_user};
                                $master_monitor_pass = $master_list->{$k_ml}->{monitor_pass};
				$master_monitor_db = $master_list->{$k_ml}->{monitor_db};
                                $master_ip = $master_list->{$k_ml}->{ip};
                                $master_db_port = $master_list->{$k_ml}->{port};
                                $master_type = $master_list->{$k_ml}->{type};
                                $master_name = $k_ml;
                                #print "$master_name -> $master_type -> $master_monitor_db -> $master_ip -> $master_db_port ->$master_monitor_user -> $master_monitor_pass \n";
                        }
                }
        }

	print "$master_name -> $master_type -> $master_monitor_db -> $master_ip -> $master_db_port ->$master_monitor_user -> $master_monitor_pass \n";

        if($slave_list->{name}){
                $slave_monitor_user = $slave_list->{monitor_user};
                $slave_monitor_pass = $slave_list->{monitor_pass};
		$slave_monitor_db = $slave_list->{monitor_db};
                $slave_ip = $slave_list->{ip};
                $slave_db_port = $slave_list->{port};
                $slave_type = $slave_list->{type};
                $slave_name = $slave_list->{name};
		$app_name = $slave_name;
                print "$slave_name -> $slave_type -> $slave_monitor_db -> $slave_ip -> $slave_db_port -> $slave_monitor_user -> $slave_monitor_pass \n";
		&monitor_mysql_master_slave();
        }else{
                foreach my $k_sl ( keys(%$slave_list)){
                        if(ref($slave_list->{$k_sl}) eq "HASH"){
                                $slave_monitor_user = $slave_list->{$k_sl}->{monitor_user};
                                $slave_monitor_pass = $slave_list->{$k_sl}->{monitor_pass};
				$slave_monitor_db = $slave_list->{$k_sl}->{monitor_db};
                                $slave_ip = $slave_list->{$k_sl}->{ip};
                                $slave_db_port = $slave_list->{$k_sl}->{port};
                                $slave_type = $slave_list->{$k_sl}->{type};
                                $slave_name = $k_sl;
				$app_name = $slave_name;
                                print "$slave_name -> $slave_type -> $slave_monitor_db -> $slave_ip -> $slave_db_port -> $slave_monitor_user -> $slave_monitor_pass \n";
				&monitor_mysql_master_slave();
                        }
                }
        }
}


sub monitor_mysql_master_slave{
	&phpdba_log("---------------------------------------------------------\n\n @ ".$app_name." @ ".get_time()." checking start!");
	&phpdba_log(&print_config());
	%ip_port_list = (
			"$master_ip"=>"$master_db_port",
			"$slave_ip"=>"$slave_db_port"
			);

	$M_dbh = &get_connect($master_ip,$master_db_port,$master_monitor_db,$master_monitor_user,$master_monitor_pass) or
		&phpdba_log("ERROR:Can't connect to MASTER!\n $app_name checking over!\n -----------------------------------------\n");
	sleep 1;
	$S_dbh = &get_connect($slave_ip,$slave_db_port,$slave_monitor_db,$slave_monitor_user,$slave_monitor_pass) or
		&phpdba_log("ERROR:Can't connect to SLAVE!\n $app_name checking over!\n -----------------------------------------\n");

	$M_connect = $M_dbh && $M_dbh->ping;
	$S_connect = $S_dbh && $S_dbh->ping;
	if($M_connect && $S_connect){
		&main();
	}
}

sub print_config{
	return "=============================\n monitor db:$master_monitor_db\n monitor ip:$master_ip \n master port:$master_db_port \n slave ip:$slave_ip\n slave port:$slave_db_port \n =============================\n";
}

sub main{
	&check_port_status();
	&phpdba_mail();
	&dbh_disconnect();
	if($send_email_status == 1){
                &phpdba_log($app_name." MySQL Slave is Error!");
        }else{
		&phpdba_log($app_name." MySQL Slave is OK!");
	}
	&phpdba_log("@ ".$app_name." @ ".get_time()." checking over! \n----------------------------------------------------------");
	$send_email_status = 0;
}

sub check_port_status{
	my $key;
	my $value;
	while(($key,$value)=each %ip_port_list){
		sleep 1;
		if(! &port_status($key,$value)){
			&phpdba_log("$key:$value Downing ...!");
			&mail_send($value,"Mysql_Port:$key","$key is Downing ...! ");
		}
	}
}

sub phpdba_mail{
	foreach my $k (@data){
		pop(@data);
	}
	#my @check_rep_status_arr = &check_rep_status();
	#print @check_rep_status_arr;
	if(my @check_rep_status_arr = &check_rep_status()){
        	foreach my $data (@check_rep_status_arr){
                	push(@data,$data);
        	}
	}

#	my $data = @data ? join('\r',@data):" ";
	if(! $M_connect){
		&mail_send($master_ip,"Mysql_Master_Ser","Mysql_Master_Ser is Downing...!");
		sleep 1;
	};
	if(! $S_connect){
		&mail_send($slave_ip,"Mysql_Slave_Ser","Mysql_Slave_ser is Downing...!");
		sleep 1;
	}
	}
	#print "\@data:@data\n";
	if(scalar(@data)>0){
		#&mail_send($slave_ip,"Replication","Replication Error ...!","$data");
		&check_master_slave_diff();
		sleep 1;
	}

	#if($send_email_status == 1){
	#	&phpdba_log($app_name." MySQL Slave is OK!");
	#}

sub phpdba_log{
	if($debug_print != 1){
		return ;
	}
	my $time = &get_time();
	my $content=$_[0];
	my $time_show = $_[1]?1:0;
  
	if($open_check_log eq "yes"){ 
		open (LOG ,'>>'.$check_log) or die "Log file: $!";
		if($time_show){
			print LOG " $time\n $content  \n";
		}else{
			print LOG " $content  \n";
		}
		close LOG;
	}
}

sub dbh_disconnect{
	$S_dbh->disconnect();
	$M_dbh->disconnect();
}

sub port_status {
	my $ip = shift;
	my $port = shift;
	my $sock = IO::Socket::INET->new(Proto=>'tcp',PeerAddr=>$ip,PeerPort=>$port,Timeout=>10);
	#phpdba_log("port_status");
	return $sock ? 1:0;
	#$sock ? return 1:return 0;
}

sub get_time {
	my $time = shift || time();
	my ($sec,$min,$hour,$day,$mon,$year,$wday) = localtime($time);
	$year += 1900;
	$mon += 1;
	$min = '0'.$min if length($min) < 2;
	$sec = '0'.$sec if length($sec) < 2;
	$mon = '0'.$mon if length($mon) < 2;
	$day = '0'.$day if length($day) < 2;
	$hour = '0'.$hour if length($hour) < 2;
	my $weekday = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat')[$wday];
	my $time_now = "$year-$mon-$day $hour:$min:$sec $weekday";
	return $time_now;
}

sub get_connect{
	my $host = shift;
	my $db_port = shift;
	my $monitor_db = shift;
	my $monitor_user = shift;
	my $monitor_pass = shift;
	my $dsn = "DBI:mysql:$monitor_db:$host:$db_port";
	#&phpdba_log($dsn);
	my $dbh = DBI->connect($dsn,$monitor_user,$monitor_pass,{RaiseError=>0,PrintError=>0});
	if(!$dbh) {
		&phpdba_log("ERROR:Can't connect to MySQL (host=$host:$db_port,user=$monitor_user)!"); 
		&mail_send("$host","MySQL Connect Error","ERROR:Can't connect to MySQL (host=$host:$db_port,user=$monitor_user)!");		
	}
	return $dbh;
}

sub check_rep_status{
	my ($error,%result,$data);
	my $sql = "Show Slave Status";
	my $sth = $S_dbh->prepare($sql);
	$sth->execute();
	%result = %{$data} while($data=$sth->fetchrow_hashref);
	$sth->finish();

	#return "ok";
	if((defined($result{'Slave_IO_Running'}) && $result{'Slave_IO_Running'} ne 'Yes') || (defined($result{'Slave_SQL_Running'}) && $result{'Slave_SQL_Running'} ne 'Yes')){
		&phpdba_log($app_name." MySQL Replication Error!\n Slave_IO_Running=".$result{'Slave_IO_Running'}."\n Slave_SQL_Running=".$result{'Slave_SQL_Running'}."\n");
		&mail_send("$slave_ip","MySQL Replication Error","\n Slave_IO_Running=".$result{'Slave_IO_Running'}."\n Slave_SQL_Running=".$result{'Slave_SQL_Running'}."\n");
		return ("Slave_IO_Running=".$result{'Slave_IO_Running'}."\nSlave_SQL_Running=".$result{'Slave_SQL_Running'});
	}

	if(defined($result{'Seconds_Behind_Master'}) && $result{'Seconds_Behind_Master'} >= $default_seconds_behind_limit){
		$error = "1004";
		return ("Seconds_Behind_Master=".$result{'Seconds_Behind_Master'});
	}

	if(defined($result{'Last_Errno'}) && $result{'Last_Errno'} != 0){
		$error = "1005";
		return ("Last_Errno=$result{'Last_Errno'}");
	}
	#return undef unless(%result);
	return undef;
}

sub check_master_slave_diff{
	my (@error,$data,%result_master,%result_slave,%result_diff);
	my @master_slave_table_diff;
	%result_slave = &get_table_count($S_dbh);
	sleep 1;
	%result_master = &get_table_count($M_dbh);

	#print "ok\n";
	while(my($key,$value) = each %result_slave){
		my $var = defined($result_master{$key})?$result_master{$key}-$value:0;
		#print $var;
		if($var >= $master_slave_table_diff_size){
			#print "table :".$key."->master[".$result_master{$key}."]/slave[".$value."]/diff:$var\n";
			push(@master_slave_table_diff,"table :".$key."->master[".$result_master{$key}."]/slave[".$value."]/diff:$var\n");
			$result_diff{$key} = $var;
		}
		#if($var>$master_slave_table_diff_size){$result_diff{$key} = $var;}
	}

	my $master_slave_table_diff_str = join(" ",@master_slave_table_diff);
	print $master_slave_table_diff_str;
	&phpdba_log($master_slave_table_diff_str) if(@master_slave_table_diff);

	while(my($k,$v)= each %result_diff){
		push(@error,$k."\t".$v);
	}

	$data = join("\n",@error);
	&mail_send($slave_ip,"Master Slave Table Diff","All Table diff :"," $master_slave_table_diff_str") if(%result_diff);
	#&mail_send($slave_ip,"Master Slave Table Diff","All Table diff !","$data") if(%result_diff);
	#sleep 1;
	return %result_diff;
}

sub get_table_count{
	my $dbh = shift;
	my ($error,%result,$data,$count_sql);
        my $sql = "show tables";
        my $sth = $dbh->prepare($sql);
        $sth->execute();
        while(my $row=$sth->fetchrow_array){
                $count_sql = "select count(*) from ".$row." limit 1";
                my $count_sth = $S_dbh->prepare($count_sql);
                $count_sth->execute();
                my $count_row = $count_sth->fetchrow_array;
                $count_sth->finish();
		#print "row: $row";
                $result{$row} = $count_row;

        }
        #%result = %{$data} while($data=$sth->fetchrow_hashref);
        $sth->finish();
	return %result;
}

sub mail_send{
	my $subject = shift;
	my $subject_ip = shift;
	my $mail = shift;
	my $data = shift;
	my $time_now = &get_time();
	my $smtp_mail_host = 'smtp.163.com';
	my $mail_user_from = 'alert@163.com';
	my $mail_user = 'alert';
	my $work_time = time();
	my $mail_user_to;
	my ($sec,$min,$hour,$day,$mon,$year,$wday) = localtime($work_time);
	if($hour>9 && $hour<17){
		$mail_user_to = 'chen-123@phpdba.com';
	}else{
		$mail_user_to = '150xxxxxxxx@139.com';
	}
	my $mail_user_pass = 'phpdbaphpdba';
	#my $mail_hello = 'mail.163.com';
	my $smtp = Net::SMTP->new(Host=>"$smtp_mail_host",timeout=>40, Debug=>0) or die "can not connect mail server";		
	$smtp->auth("$mail_user","$mail_user_pass") or die "auth failed!";
	#$smtp->mail("$mail_user_from","Mysql Replication Monitor");
	$smtp->mail("$mail_user_from");
	$smtp->to("$mail_user_to");
	$smtp->data();
	$smtp->datasend("Subject:warning:$app_name $subject_ip $subject\n");
	$smtp->datasend("From:$mail_user_from\n");
	$smtp->datasend("To:$mail_user_to\n");
	$smtp->datasend("\n");
	$smtp->datasend("Dear Noc:\n");
	$smtp->datasend("\t$subject $subject_ip\n");
	$smtp->datasend("\t$mail\n");
	$data?$smtp->datasend("\t$data\n\r"):$smtp->datasend("\n");
	$smtp->datasend("\t----------------\n");
	$smtp->datasend("$time_now\n\n\n");
	$smtp->dataend;
	$smtp->quit();	
	print get_time()." $app_name mail send successful!\n";
	$send_email_status = 1;
}
