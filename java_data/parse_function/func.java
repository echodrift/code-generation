class ReactiveLoadBalancerClientFilter implements GlobalFilter, Ordered {

	private static final Log log = LogFactory
			.getLog(ReactiveLoadBalancerClientFilter.class);

	/**
	 * Order of filter.
	 */
	public static final int LOAD_BALANCER_CLIENT_FILTER_ORDER = 10150;

	private final LoadBalancerClientFactory clientFactory;

	private final GatewayLoadBalancerProperties properties;

	/**
	 * @deprecated in favour of
	 *             {@link ReactiveLoadBalancerClientFilter#ReactiveLoadBalancerClientFilter(LoadBalancerClientFactory, GatewayLoadBalancerProperties)}
	 */
	@Deprecated
	public ReactiveLoadBalancerClientFilter(
			LoadBalancerClientFactory clientFactory,
			GatewayLoadBalancerProperties properties,
			LoadBalancerProperties loadBalancerProperties) {
		this.clientFactory = clientFactory;
		this.properties = properties;
	}

	public ReactiveLoadBalancerClientFilter(
			LoadBalancerClientFactory clientFactory,
			GatewayLoadBalancerProperties properties) {
		this.clientFactory = clientFactory;
		this.properties = properties;
	}

	@Override
	public int getOrder() {
		return LOAD_BALANCER_CLIENT_FILTER_ORDER;
	}

	@Override
	public Mono<Void> filter(ServerWebExchange exchange,
			GatewayFilterChain chain) {
		URI url = exchange.getAttribute(GATEWAY_REQUEST_URL_ATTR);
		String schemePrefix = exchange.getAttribute(GATEWAY_SCHEME_PREFIX_ATTR);
		if (url == null || (!"lb".equals(url.getScheme())
				&& !"lb".equals(schemePrefix))) {
			return chain.filter(exchange);
		}
		// preserve the original url
		addOriginalRequestUrl(exchange, url);

		if (log.isTraceEnabled()) {
			log.trace(ReactiveLoadBalancerClientFilter.class.getSimpleName()
					+ " url before: " + url);
		}

		URI requestUri = exchange.getAttribute(GATEWAY_REQUEST_URL_ATTR);
		String serviceId = requestUri.getHost();
		Set<LoadBalancerLifecycle> supportedLifecycleProcessors = LoadBalancerLifecycleValidator
				.getSupportedLifecycleProcessors(
						clientFactory.getInstances(serviceId,
								LoadBalancerLifecycle.class),
						RequestDataContext.class, ResponseData.class,
						ServiceInstance.class);
		DefaultRequest<RequestDataContext> lbRequest = new DefaultRequest<>(
				new RequestDataContext(new RequestData(exchange.getRequest(),
						exchange.getAttributes()), getHint(serviceId)));
		return choose(lbRequest, serviceId, supportedLifecycleProcessors)
				.doOnNext(response -> {

					if (!response.hasServer()) {
						supportedLifecycleProcessors
								.forEach(lifecycle -> lifecycle
										.onComplete(new CompletionContext<>(
												CompletionContext.Status.DISCARD,
												lbRequest, response)));
						throw NotFoundException.create(properties.isUse404(),
								"Unable to find instance for " + url.getHost());
					}

					ServiceInstance retrievedInstance = response.getServer();

					URI uri = exchange.getRequest().getURI();

					// if the `lb:<scheme>` mechanism was used, use `<scheme>`
					// as the default,
					// if the loadbalancer doesn't provide one.
					String overrideScheme = retrievedInstance.isSecure()
							? "https"
							: "http";
					if (schemePrefix != null) {
						overrideScheme = url.getScheme();
					}

					DelegatingServiceInstance serviceInstance = new DelegatingServiceInstance(
							retrievedInstance, overrideScheme);

					URI requestUrl = reconstructURI(serviceInstance, uri);

					if (log.isTraceEnabled()) {
						log.trace("LoadBalancerClientFilter url chosen: "
								+ requestUrl);
					}
					exchange.getAttributes().put(GATEWAY_REQUEST_URL_ATTR,
							requestUrl);
					exchange.getAttributes()
							.put(GATEWAY_LOADBALANCER_RESPONSE_ATTR, response);
					supportedLifecycleProcessors.forEach(lifecycle -> lifecycle
							.onStartRequest(lbRequest, response));
				}).then(chain.filter(exchange))
				.doOnError(throwable -> supportedLifecycleProcessors
						.forEach(lifecycle -> lifecycle.onComplete(
								new CompletionContext<ResponseData, ServiceInstance, RequestDataContext>(
										CompletionContext.Status.FAILED,
										throwable, lbRequest,
										exchange.getAttribute(
												GATEWAY_LOADBALANCER_RESPONSE_ATTR)))))
				.doOnSuccess(aVoid -> supportedLifecycleProcessors
						.forEach(lifecycle -> lifecycle.onComplete(
								new CompletionContext<ResponseData, ServiceInstance, RequestDataContext>(
										CompletionContext.Status.SUCCESS,
										lbRequest,
										exchange.getAttribute(
												GATEWAY_LOADBALANCER_RESPONSE_ATTR),
										new ResponseData(exchange.getResponse(),
												new RequestData(
														exchange.getRequest(),
														exchange.getAttributes()))))));
	}

	protected URI reconstructURI(ServiceInstance serviceInstance,
			URI original) {
		return LoadBalancerUriTools.reconstructURI(serviceInstance, original);
	}

	private Mono<Response<ServiceInstance>> choose(
			Request<RequestDataContext> lbRequest, String serviceId,
			Set<LoadBalancerLifecycle> supportedLifecycleProcessors) {
		LoadBalancerProperties loadBalancerProperties = clientFactory
				.getProperties(serviceId);
		LoadBalancerClient loadBalancer = clientFactory
				.getLazyProvider(serviceId, loadBalancerProperties)
				.getIfAvailable();

		return loadBalancer.choose(lbRequest)
				.doOnNext(response -> supportedLifecycleProcessors.forEach(
						lifecycle -> lifecycle.onStart(lbRequest, response)));
	}

	private String getHint(String serviceId) {
		LoadBalancerProperties loadBalancerProperties = clientFactory
				.getProperties(serviceId);
		Map<String, String> hints = loadBalancerProperties.getHint();
		String defaultHint = hints.getOrDefault("default", "default");
		String hintPropertyValue = hints.get(serviceId);
		return hintPropertyValue != null ? hintPropertyValue : defaultHint;
	}

}