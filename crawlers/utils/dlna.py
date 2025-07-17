
import asyncio
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.client_factory import UpnpFactory
import requests
import logging

class Dlna:
  
    async def dlna_list(self):
        try:
    # 发送GET请求
            response = requests.get("http://192.168.31.1:8012/getDeviceList?666888", timeout=5)  # 设置超时时间
    
    # 检查HTTP状态码
            response.raise_for_status()  # 如果状态码不是200，抛出异常
    
    # 解析JSON响应
            json_data = response.json()
    
            return json_data    
    # 示例：访问JSON中的特定字段（假设返回结构包含"data"字段）
    # if "data" in json_data:
    #     print("\nData字段内容:", json_data["data"])

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
       
        except ValueError as ve:
            print(f"JSON解析失败: {ve}\n原始响应文本:\n{response.text}")
    async def play_dlna(self,dmrUrl: str,dstUrl:str=""):
            print(dmrUrl,dstUrl)
            requester = AiohttpRequester()
            factory = UpnpFactory(requester)
            device = await factory.async_create_device(dmrUrl)

    # 2. 获取AVTransport服务
            avt_service = device.service("urn:schemas-upnp-org:service:AVTransport:1")
            if not avt_service:
                raise RuntimeError("DMR不支持AVTransport服务！")

    # 3. 设置媒体资源URI
            await avt_service.async_call_action(
                "SetAVTransportURI",
                InstanceID=0,
                CurrentURI=dstUrl,
                CurrentURIMetaData="",  # 元数据（可选）
            )

    # 4. 播放
            await avt_service.async_call_action("Play", InstanceID=0, Speed="1")
    async def main(self):
        # 占位
        pass


if __name__ == '__main__':
    # 实例化混合爬虫/Instantiate hybrid crawler
    print(111)


async def dlna_list():
    try:
    # 发送GET请求
        response = requests.get("http://192.168.31.1:8012/getDeviceList?666888", timeout=5)  # 设置超时时间
    
    # 检查HTTP状态码
        response.raise_for_status()  # 如果状态码不是200，抛出异常
    
    # 解析JSON响应
        json_data = response.json()
    
        return json_data    
    # 示例：访问JSON中的特定字段（假设返回结构包含"data"字段）
    # if "data" in json_data:
    #     print("\nData字段内容:", json_data["data"])

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
       
    except ValueError as ve:
        print(f"JSON解析失败: {ve}\n原始响应文本:\n{response.text}")
async def play_dlna(dmrUrl: str,dstUrl:str=""):
    requester = AiohttpRequester()
    factory = UpnpFactory(requester)
    device = await factory.async_create_device(dmrUrl)

    # 2. 获取AVTransport服务
    avt_service = device.service("urn:schemas-upnp-org:service:AVTransport:1")
    if not avt_service:
        raise RuntimeError("DMR不支持AVTransport服务！")

    # 3. 设置媒体资源URI
    await avt_service.async_call_action(
        "SetAVTransportURI",
        InstanceID=0,
        CurrentURI=dstUrl,
        CurrentURIMetaData="",  # 元数据（可选）
    )

    # 4. 播放
    await avt_service.async_call_action("Play", InstanceID=0, Speed="1")


# 全局状态管理器
class DLNAPlayer:
    def __init__(self):
        self.devices = {}
        self.lock = asyncio.Lock()
        self.requester = AiohttpRequester(timeout=30)
        self.factory = UpnpFactory(self.requester)
        self.logger = logging.getLogger("DLNAPlayer")
    
    async def get_device(self, dmr_url: str):
        """设备连接复用（带锁）"""
        async with self.lock:
            if dmr_url in self.devices:
                return self.devices[dmr_url]
            
            try:
                device = await self.factory.async_create_device(dmr_url)
                self.devices[dmr_url] = device
                self.logger.info(f"设备连接成功: {dmr_url}")
                return device
            except Exception as e:
                self.logger.error(f"设备连接失败: {dmr_url} - {e}")
                raise ConnectionError(f"无法连接设备: {e}")

    async def play(self, dmr_url: str, media_url: str):
        """核心播放逻辑（带状态监控）"""
        device = await self.get_device(dmr_url)
        avt_service = device.service("urn:schemas-upnp-org:service:AVTransport:1")
        
        if not avt_service:
            raise RuntimeError("设备不支持AVTransport服务")
        
        # 1. 设置媒体URI
        await avt_service.async_call_action(
            "SetAVTransportURI",
            InstanceID=0,
            CurrentURI=media_url,
            CurrentURIMetaData='<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><item><res protocolInfo="http-get:*:*:*"></res></item></DIDL-Lite>'
        )
        
        # 2. 启动播放
        await avt_service.async_call_action("Play", InstanceID=0, Speed="1")
        
        # 3. 后台状态监控
        asyncio.create_task(self._monitor_playback(avt_service))
        
        return {"status": "playing", "media": media_url}
    
    async def _monitor_playback(self, avt_service):
        """播放状态监控和自动恢复"""
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                # 获取当前播放状态
                state_var = await avt_service.async_get_state_variable("TransportState")
                self.logger.debug(f"播放状态: {state_var.value}")
                
                if state_var.value == "PLAYING":
                    retry_count = 0  # 重置重试计数器
                    continue
                
                # 状态异常时尝试恢复
                self.logger.warning(f"播放中断，尝试恢复 (重试 {retry_count+1}/{max_retries})")
                # await avt_service.async_call_action("Play", InstanceID=0, Speed="1")
                retry_count += 1
                
            except Exception as e:
                self.logger.error(f"状态监控错误: {e}")
                retry_count += 1
        
        self.logger.error("播放恢复失败，终止监控")