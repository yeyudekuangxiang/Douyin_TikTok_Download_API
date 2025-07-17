
import asyncio
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.client_factory import UpnpFactory
import requests


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
    dlna = Dlna()
    # 运行测试代码/Run test code
    asyncio.run(dlna.main())


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