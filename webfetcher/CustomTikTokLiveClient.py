# 重新部分数据 方便书写业务逻辑
import websocket
from webfetcher.TikTokLiveClient import *
# 桥
from units.Bridge import *

# 队列
from units.EventHandler import *


class CustomTikTokLiveClient(TikTokLiveClient):
    def __init__(self, live_id):
        # 调用父类的初始化方法
        super().__init__(live_id)  # 如果父类需要传参，在这里传入

        # 创建信号对象
        self.log_signals = LogSignals()

    def log(self, message):
        """
        线程安全的日志记录方法
        """
        # 发送信号，由主线程处理日志显示
        self.log_signals.log_signal.emit(message)

    # 当前重写部分-消息监听
    def _wsOnMessage(self, ws, message):
        """
        接收到数据
        :param ws: websocket实例
        :param message: 数据
        """

        # 根据proto结构体解析对象
        package = PushFrame().parse(message)
        response = Response().parse(gzip.decompress(package.payload))

        # 返回直播间服务器链接存活确认消息，便于持续获取数据
        if response.need_ack:
            ack = PushFrame(log_id=package.log_id,
                            payload_type='ack',
                            payload=response.internal_ext.encode('utf-8')
                            ).SerializeToString()
            ws.send(ack, websocket.ABNF.OPCODE_BINARY)

        # 根据消息类别解析消息体
        for msg in response.messages_list:
            method = msg.method
            try:
                {
                    'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                    'WebcastGiftMessage': self._parseGiftMsg,  # 礼物消息
                    # 'WebcastLikeMessage': self._parseLikeMsg,  # 点赞消息
                    'WebcastMemberMessage': self._parseMemberMsg,  # 进入直播间消息
                    # 'WebcastSocialMessage': self._parseSocialMsg,  # 关注消息
                    # 'WebcastRoomUserSeqMessage': self._parseRoomUserSeqMsg,  # 直播间统计
                    # 'WebcastFansclubMessage': self._parseFansclubMsg,  # 粉丝团消息
                    # 'WebcastControlMessage': self._parseControlMsg,  # 直播间状态消息
                    # 'WebcastEmojiChatMessage': self._parseEmojiChatMsg,  # 聊天表情包消息
                    # 'WebcastRoomStatsMessage': self._parseRoomStatsMsg,  # 直播间统计信息
                    # 'WebcastRoomMessage': self._parseRoomMsg,  # 直播间信息
                    # 'WebcastRoomRankMessage': self._parseRankMsg,  # 直播间排行榜信息
                }.get(method)(msg.payload)
            except Exception:
                pass

    # 收到弹幕
    def _parseChatMsg(self, payload):
        """聊天消息"""
        message = ChatMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        content = message.content
        print(f"【聊天】[{user_id}]{user_name}: {content}")
        self.log(f"【聊天】[{user_id}]{user_name}: {content}")
        # 新增对话
        action = {f'comment': f'{message.content}'}
        handler.add_to_queue(action)

    # 礼物信息
    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        user_name = message.user.nick_name
        gift_name = message.gift.name
        gift_cnt = message.combo_count
        print(f"【礼物】{user_name} 送出了 {gift_name}x{gift_cnt}")
        self.log(f"【礼物】{user_name} 送出了 {gift_name}x{gift_cnt}")
        # 播报礼物
        action = {f'broadcast': f'感谢{user_name}送的{gift_cnt}个{gift_name}'}
        handler.add_to_queue(action)
        # 新增礼物
        action = {f'gift': f'{gift_name}'}
        handler.add_to_queue(action)



    # 进入直播间
    def _parseMemberMsg(self, payload):
        '''进入直播间消息'''
        message = MemberMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        gender = ["女", "男"][message.user.gender]
        print(f"【进场msg】[{user_id}][{gender}]{user_name} 进入了直播间")
        # 播报进场
        action = {f'broadcast': f'欢迎{user_name}进入直播间！'}
        handler.add_to_queue(action)
