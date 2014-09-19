<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed'); ?>

<div class="page-header">
  <h2>添加主机<small></small></h2>
</div>
  
<div class="btn-toolbar">
                <div class="btn-group">
                  <a class="btn btn-default active" href="<?php echo site_url('servers/add') ?>">&nbsp;新增</a>
                  <a class="btn btn-default " href="<?php echo site_url('servers/batch_add') ?>">&nbsp;批量新增</a>
                  <a class="btn btn-default " href="<?php echo site_url('servers/index') ?>">&nbsp;列表</a>
                  <a class="btn btn-default " href="<?php echo site_url('servers/trash') ?>">&nbsp;回收站</a>
                </div>
</div> <!-- /toolbar -->               
<hr/>                

<?php if ($error_code!==0) { ?>
<div class="ui-widget">
<div class="ui-state-error   ui-corner-all">
<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>
<?php echo validation_errors(); ?></p>
</div>
</div>

<?php } ?>

<form name="form" class="form-horizontal" method="post" action="<?php echo site_url('servers/add') ?>" >
<input type="hidden" name="submit" value="add"/> 
   
    <div class="control-group">
    <label class="control-label" for="">*主机</label>
    <div class="controls">
      <input type="text" id=""  name="host" value="<?php echo set_value('host'); ?>" >
      <span class="help-inline">服务器内网IP</span>
    </div>
   </div>
   <div class="control-group">
    <label class="control-label" for="">*主机别名</label>
    <div class="controls">
      <input type="text" id=""  name="alias_host" value="<?php echo set_value('alias_host'); ?>" >
      <span class="help-inline">服务器外网IP</span>
    </div>
   </div>
   <div class="control-group">
    <label class="control-label" for="">*端口</label>
    <div class="controls">
      <input type="text" id=""  name="port" value="<?php echo set_value('port','3306'); ?>" >
      <span class="help-inline">数据库开启端口</span>
    </div>
   </div>
   <div class="control-group">
    <label class="control-label" for="">*机房</label>
    <div class="controls">
        <select name="idc_type" id="idc_type" >
         <option value="yf"  selected="selected">西街机房</option>
         <option value="ts">新村机房</option>
        </select>
        <span class="help-inline">选择服务器所在机房，内网ip 。</span>
    </div>
   </div>
   <div class="control-group">
    <label class="control-label" for="">选择应用</label>
    <div class="controls">
        <select name="application_id" id="application_id">
        <option value=""  >选择应用</option>
        <?php if(!empty($application)) {?>
        <?php foreach ($application  as $item):?>
         <option value="<?php echo $item['id']?>"  ><?php echo $item['name']?>(<?php echo $item['display_name']?>)</option>
        <?php endforeach;?>
        <?php } ?>
        </select>
        <span class="help-inline">属于同一节点的Master/Slave服务器请选择为相同的应用</span>
    </div>
   </div> 
   <div class="control-group">
    <label class="control-label" for="">慢查询分析</label>
    <div class="controls">
        <select name="slow_query" id="slow_query" class="input-small">
         <option value="1"  >开启</option>
         <option value="0" selected="selected" >关闭</option>
        </select>
        <span class="help-inline">该主机未配置慢查询采集脚本前请勿开启本选项，请在配置后再启用本选项。</span>
    </div>
   </div>
    <div class="control-group">
    <label class="control-label" for="">监控状态</label>
    <div class="controls">
        <select name="status" id="status" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
    </div>
   </div>
    <div class="control-group">
    <label class="control-label" for="">发送告警邮件</label>
    <div class="controls">
        <select name="send_mail" id="send_mail" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
    </div>
   </div>
    <div class="control-group">
    <label class="control-label" for="">总连接数告警</label>
    <div class="controls">
        <select name="alarm_connections" id="alarm_connections" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
        告警阀值&nbsp;<input type="text" id="threshold_connections" class="input-small" placeholder="告警阀值" name="threshold_connections" value="1000" >
    </div>
   </div>
    <div class="control-group">
    <label class="control-label" for="">活动进程告警</label>
    <div class="controls">
        <select name="alarm_active" id="alarm_active" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
        告警阀值&nbsp;<input type="text" id="threshold_active" class="input-small" placeholder="告警阀值" name="threshold_active" value="10" >
    </div>
   </div>

	<div class="control-group">
    <label class="control-label" for="">告警时间段</label>
    <div class="controls">
        <select name="alarm_time" id="alarm_time" class="input-small">
         <option value="1" >开启</option>
         <option value="0" selected="selected" >关闭</option>
        </select>
        开始时间&nbsp;<input type="text" id="threshold_starttime" class="input-small" placeholder="开始时间" name="threshold_starttime" value="09:00" >
        结束时间&nbsp;<input type="text" id="threshold_endtime" class="input-small" placeholder="结束时间" name="threshold_endtime" value="23:00" >
    </div>
   </div>

    <div class="control-group">
    <label class="control-label" for="">复制状态告警</label>
    <div class="controls">
        <select name="alarm_repl_status" id="alarm_repl_status" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
    </div>
   </div>
    <div class="control-group">
    <label class="control-label" for="">复制延时告警</label>
    <div class="controls">
        <select name="alarm_repl_delay" id="alarm_repl_delay" class="input-small">
         <option value="1"  >开启</option>
         <option value="0"  >关闭</option>
        </select>
        告警阀值&nbsp;<input type="text" id="threshold_repl_delay" class="input-small" placeholder="告警阀值" name="threshold_repl_delay" value="60" >
    </div>
   </div>
   

  <div class="control-group">
    <div class="controls">
      <button type="submit" class="btn btn-success">提 交</button> &nbsp;我想放弃提交，<a href='<?php echo site_url('servers/index')?>'>点此返回</a>    
    </div>
  </div>
                                    
</form>

