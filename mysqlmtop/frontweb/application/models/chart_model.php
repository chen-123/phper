<?php 
class Chart_model extends CI_Model{

    


    
    function get_status($server_id,$time,$limit=30){
	$YmdHi = date("YmdHi",strtotime($time));
        $query=$this->db->query("select active,connections,QPS,TPS,Bytes_received,Bytes_sent,a.create_time from mysql_status_history a  join mysql_status_ext_history b on a.server_id=b.server_id and a.server_id=$server_id and a.YmdHi=b.YmdHi and a.YmdHi>='${YmdHi}' limit ${limit}; ");
	
        if ($query->num_rows() > 0)
        {
	   return $query->result_array();
           //return $query->row_array(); 
        }
    }
    
    function get_status_ext($server_id,$time){
	$YmdHi = date("YmdHi",strtotime($time));
        $query=$this->db->query("select QPS,TPS,Bytes_received,Bytes_sent,create_time from mysql_status_ext_history where YmdHi>='$YmdHi' and server_id=$server_id limit 30; ");
        if ($query->num_rows() > 0)
        {
	   return $query->result_array();
           //return $query->row_array(); 
        }
    }
    
    function get_replication($server_id,$time,$limit=1){
        $query=$this->db->query("select slave_io_run,slave_sql_run,delay,create_time from mysql_replication_history where server_id=$server_id and YmdHi>='$time' limit ${limit}; ");
        if ($query->num_rows() > 0)
        {
	   return $query->result_array();
           //return $query->row_array(); 
        }
    }
    

}

/* End of file mysql_model.php */
/* Location: ./application/models/mysql_model.php */
