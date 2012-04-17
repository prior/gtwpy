from utils.property import is_cached
from utils.list import sort
from utils.obj import mgetattr

class Base(object):

    def _cmp_components(self, other, *attrs):
        for a in attrs:
            result = cmp(getattr(self, a, None), getattr(other, a, None))
            if result != 0: return result
        return 0

    def merge(self, *others): raise NotImplementedError()

    def _merge_primitives(self, other, *attrs):
        for a in attrs: 
            if getattr(other, a, None) is not None: setattr(self, a, getattr(other, a))
        return self

    def _merge_cached_exchange_collection(self, other, attr, keys=None, session_match=False):
        ex_attr = '_%s_ex'%attr
        if is_cached(other, ex_attr): setattr(self, ex_attr, getattr(other, ex_attr))
        if not is_cached(other, attr): 
            return
        if not is_cached(self, attr):
            setattr(self, attr, getattr(other, attr))
            return

        if not isinstance(keys[0], tuple): keys = [(k,) for k in keys]

        this_list = getattr(self, attr)
        that_list = getattr(other, attr)
        this_set = set(this_list)
        that_set = set(that_list)

        that_dicts = {}
        for k in keys:
            that_dicts[k] = dict((mgetattr(item,k),item) for item in getattr(other, attr) if mgetattr(item,k,None) != mgetattr(item,'',None))

        for this_item in this_list:
            that_item = None
            for k in keys:
                key_value = mgetattr(this_item, k, None)
                if key_value != mgetattr(this_item,'',None) and that_dicts[k].has_key(key_value):
                    that_item = that_dicts[k][key_value]
                    break
            if that_item:
                this_item.merge(that_item)
                that_set.remove(that_item)
                this_set.remove(this_item)

        if session_match:
            for that_item in list(that_set):
                for this_item in list(this_set):
                    if this_item.overlaps(that_item):
                        this_item.merge(that_item)
                        that_set.remove(that_item)
                        this_set.remove(this_item)
                        break;
            if len(that_set) == 1 and len(this_set) == 1:
                list(this_set)[0].merge(list(that_set)[0])
                that_set.clear()
            #else give up and just treat them all as different sessions
        this_list.extend(that_set)
        if session_match:
            for that in that_set: that.webinar = self

        setattr(self,attr,sort(this_list))
        return getattr(self,attr)

