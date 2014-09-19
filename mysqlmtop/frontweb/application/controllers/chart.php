<?php if ( ! defined("BASEPATH")) exit("No direct script access allowed");

class Chart extends Front_Controller {

    function __construct(){
		parent::__construct();
		$this->load->model("monitor_model","monitor");
        $this->load->model('application_model','app');
        $this->load->model('servers_model','server');
        $this->load->model('chart_model','chart');
        
	}

    
    public function index(){
        
        $data["server"]=$servers=$this->server->get_total_record_usage();
        $server_id = $this->uri->segment(3);
        $server_id=!empty($server_id) ? $server_id : "";

        if(empty($server_id)){
            if(!empty($servers)){
            $server_id=$servers[0]['id'];
            }
            else{
                $server_id=0;
            }
        }
        
        //连接数图表
        $reslut_status=array();
	$timestamp = time()-1920;
	$time = date('Y-m-d H:i',$timestamp);
	$dbdata=$this->chart->get_status($server_id,$time);
	foreach($dbdata as $key=>$value){
                $tmp_time = explode(" ",$value['create_time']);
                $tmp['time'] = substr($tmp_time[1],0,-3);
		/*
                $tmp['qps'] = $value['QPS'];
                $tmp['tps'] = $value['TPS'];
                $tmp['Bytes_received'] = $value['Bytes_received'];
                $tmp['Bytes_sent'] = $value['Bytes_sent'];
		*/
		$tmp['connections'] = $value['connections'];
		$tmp['active'] = $value['active'];
                $reslut_status[] = $tmp;
        }

	//var_dump($reslut_status);die();

	/*
        for($i=30;$i>=0;$i--){
            $timestamp=time()-60*$i;
            $time= date('Y-m-d H:i',$timestamp);
            $reslut_status[$i]['time']=date('H:i',$timestamp);
            $dbdata=$this->chart->get_status($server_id,$time);//连接数 未获取到

            $reslut_status[$i]['connections'] = $dbdata['connections'];
            $reslut_status[$i]['active'] = $dbdata['active'];
            
        }
	*/

        //print_r($reslut_active);exit;
        $data['reslut_status']=$reslut_status;

        $reslut_status_ext=array();
	$timestamp = time()-1920;
	$time = date('Y-m-d H:i',$timestamp);
	$dbdata_ext = $this->chart->get_status_ext($server_id,$time);
	foreach($dbdata_ext as $key_ext=>$value_ext){
		$tmp_time = explode(" ",$value_ext['create_time']);
		$tmp['time'] = substr($tmp_time[1],0,-3);
		$tmp['qps'] = $value_ext['QPS'];
		$tmp['tps'] = $value_ext['TPS'];
		$tmp['Bytes_received'] = $value_ext['Bytes_received'];
		$tmp['Bytes_sent'] = $value_ext['Bytes_sent'];
		$reslut_status_ext[] = $tmp;
	}

	/*
        for($i=30;$i>=0;$i--){
            $timestamp=time()-60*$i;
            $time= date('Y-m-d H:i',$timestamp);
            $reslut_status_ext[$i]['time']=date('H:i',$timestamp);
            $dbdata=$this->chart->get_status_ext($server_id,$time);
            $reslut_status_ext[$i]['qps'] = $dbdata['QPS'];
            $reslut_status_ext[$i]['tps'] = $dbdata['TPS'];
            $reslut_status_ext[$i]['Bytes_received'] = $dbdata['Bytes_received'];
            $reslut_status_ext[$i]['Bytes_sent'] = $dbdata['Bytes_sent'];
            
        }
	*/

        //print_r($reslut_active);exit;
        $data['reslut_status_ext']=$reslut_status_ext;
        $data['cur_nav']='chart_index';
        $data['cur_server_id']=$server_id;
        $data["cur_server"] = $this->server->get_servers($server_id);
        $this->layout->view('chart/index',$data);
    }
    
    public function status(){
        
        $server_id = $this->uri->segment(3);
        $server_id=!empty($server_id) ? $server_id : "0";
        $begin_time = $this->uri->segment(4);
        $begin_time=!empty($begin_time) ? $begin_time : "60";
        $time_span = $this->uri->segment(5);
        $time_span=!empty($time_span) ? $time_span : "hour";
       
        //连接数图表
        $chart_reslut = array();   
	$timestamp = time() - 60*$begin_time;
        $time = date('Y-m-d H:i',$timestamp);
        $dbdata=$this->chart->get_status($server_id,$time,$begin_time);
        foreach($dbdata as $key=>$value){
                $tmp_time = explode(" ",$value['create_time']);
                $tmp['time'] = substr($value['create_time'],0,-3);
                $tmp['QPS'] = $value['QPS'];
                $tmp['TPS'] = $value['TPS'];
                $tmp['Bytes_received'] = $value['Bytes_received'];
                $tmp['Bytes_sent'] = $value['Bytes_sent'];
                $tmp['connections'] = $value['connections'];
                $tmp['active'] = $value['active'];
                $chart_reslut[] = $tmp;
        }
	/*           
        for($i=$begin_time;$i>=0;$i--){
            $timestamp=time()-60*$i;
            $time= date('YmdHi',$timestamp);
            $chart_reslut[$i]['time']=date('Y-m-d H:i',$timestamp);
            $dbdata=$this->chart->get_status($server_id,$time);
            $chart_reslut[$i]['active'] = $dbdata['active'];
            $chart_reslut[$i]['connections'] = $dbdata['connections']; 
            $chart_reslut[$i]['QPS'] = $dbdata['QPS'];
            $chart_reslut[$i]['TPS'] = $dbdata['TPS'];
            $chart_reslut[$i]['Bytes_received'] = $dbdata['Bytes_received'];
            $chart_reslut[$i]['Bytes_sent'] = $dbdata['Bytes_sent'];  
        }
	*/
	
	#var_dump($chart_reslut);die();
        $data['chart_reslut']=$chart_reslut;
    
        $chart_option=array();
        if($time_span=='hour'){
            $chart_option['formatString']='%H:%M';
        }
        else if($time_span=='day'){
            $chart_option['formatString']='%m/%d %H:%M';
        }
        
        $data['chart_option']=$chart_option;
      
        $data['begin_time']=$begin_time;
        $data['cur_nav']='chart_index';
        $data["server"]=$servers=$this->server->get_total_record_slave();
        $data['cur_server_id']=$server_id;
        $data["cur_server"] = $this->server->get_servers($server_id);
        $this->layout->view('chart/status',$data);
    }
    
    public function replication(){
        
        $server_id = $this->uri->segment(3);
        $server_id=!empty($server_id) ? $server_id : "0";
        $begin_time = $this->uri->segment(4);
        $begin_time=!empty($begin_time) ? $begin_time : "60";
        $time_span = $this->uri->segment(5);
        $time_span=!empty($time_span) ? $time_span : "hour";
        
        //连接数图表
        $chart_reslut=array();
	$timestamp = time() - 60*$begin_time;
        $time= date('YmdHi',$timestamp);
        $dbdata=$this->chart->get_replication($server_id,$time,$begin_time);
        foreach($dbdata as $key=>$value){
                $tmp['time'] = substr($value['create_time'],0,-3);
                $tmp['delay'] = $value['delay'];
                $chart_reslut[] = $tmp;
        }

	/* 
        for($i=$begin_time;$i>=0;$i--){
            $timestamp=time()-60*$i;
            $time= date('YmdHi',$timestamp);
            $chart_reslut[$i]['time']=date('Y-m-d H:i',$timestamp);
            $dbdata=$this->chart->get_replication($server_id,$time);
            $chart_reslut[$i]['delay'] = $dbdata['delay'];   
        }
	*/

        $data['chart_reslut']=$chart_reslut;
    
        $chart_option=array();
        if($time_span=='hour'){
            $chart_option['formatString']='%H:%M';
        }
        else if($time_span=='day'){
            $chart_option['formatString']='%m/%d %H:%M';
        }
        
        $data['chart_option']=$chart_option;
      
        $data['begin_time']=$begin_time;
        $data['cur_nav']='chart_index';
        $data["server"]=$servers=$this->server->get_total_record_slave();
        $data['cur_server_id']=$server_id;
        $data["cur_server"] = $this->server->get_servers($server_id);
        $this->layout->view('chart/replication',$data);
    }
    
    public function detail(){

        $server_id=$this->uri->segment(3);
        if(!$server_id){
            $server_id=$_GET['server_id'];
            $time=$_GET['time'];
        }
        
        
        
        //echo $server_id;exit;
        if(empty($server_id)){
            redirect(site_url('chart/index'));
        }
        if(empty($time)){
            $time=3600;
        }
        $data["server"]=$this->server->get_total_record_usage();
        $data["server_id"]=$server_id;
        $data["time"]=$time;
        $data['cur_nav']='chart_index';
        $this->layout->view('chart/detail',$data);
    }
    
}

/* End of file chart.php */
/* Location: ./application/controllers/chart.php */
